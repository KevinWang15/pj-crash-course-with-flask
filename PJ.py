#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, request, redirect, flash, g

import mysql.connector
import json
import hashlib

app = Flask(__name__, static_url_path='')
app.secret_key = '123456'

dbConnection = mysql.connector.connect(host='127.0.0.1', port=3306, password="", user='root', database='pj')


def get_model(table_name, attributes, sql_override=None):
    def func(id):
        if (id == None): return None

        cursor = dbConnection.cursor()
        cursor.execute(sql_override if sql_override is not None else 'select ' + ','.join(
            attributes) + ' from ' + table_name + ' where id=%s',
                       [id])
        result = cursor.fetchall()
        if len(result) == 0:
            return None
        else:
            ret = {}
            for i in range(0, len(attributes)):
                ret[attributes[i]] = result[0][i]

            return ret

    return func


get_user = get_model('user', ['id', 'name', 'password', 'user_type'])
get_post = get_model('post', ['id', 'title', 'content', 'time', 'name'],
                     'select post.id,title,content,time,user.name from `post` left join user on user.id = user_id where post.id=%s')


def get_authed_user():
    return get_user(session.get('user_id', None))


@app.before_request
def before_request():
    # g 可以理解为在所有的Jinja模板中可访问的“全局空间”，
    # 在每次request开始时，获得当前已Login的用户
    # 在所有模板中，就可以用 {{ g.authedUser }} 来访问当前用户了！
    g.authedUser = get_authed_user()
    g.url_path = request.path


@app.route('/auth/logout')
def page_logout():
    flash(u'登出成功', 'success')
    del session['user_id']
    return redirect('/')


@app.route('/new')
def page_form():
    return render_template('new.html')


@app.route('/new', methods=['POST'])
def page_form_post():
    if (len(request.form['title']) < 5):
        flash(u'标题太短了！', 'error')
        return redirect('/new')

    flash(u'添加成功！', 'success')

    cursor = dbConnection.cursor();
    cursor.execute("INSERT into post (title,content,user_id,time) values (%s,%s,%s,now())",
                   [request.form['title'], request.form['content'], session['user_id']])

    return redirect('/')


@app.route('/')
def page_list():
    cursor = dbConnection.cursor()
    cursor.execute('select id,title,time from `post` order by id desc')

    list = []

    for (id, title, time) in cursor.fetchall():
        list.append({"id": id, "title": title, "time": time})

    return render_template('list.html', list=list)


@app.route("/", methods=["POST"])
def page_list_post():
    if request.form['delete'] != None:

        user = get_authed_user()
        if user['user_type'] != 1:
            flash(u"No privilege", 'error')
            return redirect('/')

        cursor = dbConnection.cursor()
        cursor.execute('delete from post where id = %s', [request.form['delete']])

        flash(u"删除成功！", 'success')
        return redirect('/')

    else:
        flash(u"action not supported", 'error')
        return redirect('/')


@app.route("/item/<id>")
def page_item(id):
    post = get_post(id)
    return render_template("item.html", post=post)


@app.route("/item/<id>", methods=["POST"])
def page_item_post(id):
    if request.form['action'] == 'delete':

        user = get_authed_user()
        if user['user_type'] != 1:
            flash(u"No privilege", 'error')
            return redirect('/item/' + id)

        cursor = dbConnection.cursor()
        cursor.execute('delete from post where id = %s', [id])

        flash(u"删除成功！", 'success')
        return redirect('/')

    else:
        flash(u"action not supported", 'error')
        return redirect('/item/' + id)


@app.route('/auth/login')
def page_login():
    return render_template("auth/login.html")


@app.route('/auth/register')
def page_register():
    return render_template("auth/register.html")


@app.route('/auth/login', methods=["POST"])
def page_login_post():
    username = request.form['username']
    password = request.form['password']
    cursor = dbConnection.cursor()
    cursor.execute('select id,password from `user` where name=%s', [username])

    result = cursor.fetchall()
    if len(result) == 0:
        flash(u"找不到该用户", 'error')
        return redirect('/auth/login')

    if md5Hash(password) != result[0][1]:
        flash(u"密码错误", 'error')
        return redirect('/auth/login')

    session['user_id'] = result[0][0]

    flash(u"欢迎：" + username + u"。登入成功！", 'success')
    return redirect('/')
    # return render_template("auth/login.html")


@app.route('/auth/register', methods=["POST"])
def page_register_post():
    if len(request.form['username']) < 3:
        flash(u'用户名太短了！', 'error')
        return redirect('/auth/register')

    if request.form['password'] != request.form['password-repeat']:
        flash(u"两次密码不一致", 'error')
        return redirect('/auth/register')

    if len(request.form['password']) < 6:
        flash(u'密码太短了！', 'error')
        return redirect('/auth/register')

    cursor = dbConnection.cursor()

    cursor.execute('select count(1) from `user` where name=%s',
                   [request.form['username']])

    if cursor.fetchall()[0][0] > 0:
        flash(u'用户名已经被注册！', 'error')
        return redirect('/auth/register')

    cursor = dbConnection.cursor()

    cursor.execute('insert into `user` (name,password) values (%s,%s)',
                   [request.form['username'], md5Hash(request.form['password'])])

    flash(u"注册成功!", 'success')

    session['user_id'] = cursor.lastrowid

    return redirect('/')


def md5Hash(password):
    m = hashlib.md5()
    m.update(password)
    return m.hexdigest()


if __name__ == '__main__':
    app.run(debug=True)
