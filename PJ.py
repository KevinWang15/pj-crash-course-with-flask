#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, request, redirect, flash
import mysql.connector
import json
import hashlib

app = Flask(__name__, static_url_path='')
app.secret_key = '123456'

dbConnection = mysql.connector.connect(host='127.0.0.1', port=3306, password="", user='root', database='pj')


def get_user(user_id):
    if (user_id == None): return None
    cursor = dbConnection.cursor()
    cursor.execute('select id,name,password,user_type from `user` where id=%s', [user_id])
    result = cursor.fetchall()
    if len(result) == 0:
        return None
    else:
        user = result[0]
        return {"id": user[0], "name": user[1], "password": user[2], "user_type": user[3]}


def get_post(post_id):
    if (post_id == None): return None
    cursor = dbConnection.cursor()
    cursor.execute(
        'select post.id,title,content,time,user.name from `post` left join user on user.id = user_id where post.id=%s',
        [post_id])
    result = cursor.fetchall()

    if len(result) == 0:
        return None
    else:
        post = result[0]
        return {"id": post[0], "title": post[1], "content": post[2], "time": post[3], "name": post[4]}


@app.route('/simulate-login')
def page_simulate_login():
    session['user_id'] = 1
    return redirect('/')


@app.route('/logout')
def page_logout():
    flash(u'登出成功', 'success')
    del session['user_id']
    return redirect('/')


@app.route('/form')
def page_form():
    return render_template('form.html')


@app.route('/form', methods=['POST'])
def page_form_post():
    if (len(request.form['title']) < 5):
        flash(u'标题太短了！', 'error')
        return redirect('/')

    flash(u'添加成功！标题是' + request.form['title'], 'success')

    cursor = dbConnection.cursor();
    cursor.execute("INSERT into post (title,content,user_id,time) values (%s,%s,%s,now())",
                   [request.form['title'], request.form['content'], session['user_id']])

    return redirect('/form')


@app.route('/')
def page_index():
    return render_template('welcome.html', user=getCurrentlyLoggedInUser())


def getCurrentlyLoggedInUser():
    return get_user(session.get('user_id', None))


@app.route('/list')
def page_list():
    cursor = dbConnection.cursor()
    cursor.execute('select id,title,content,time from `post` order by id desc')

    list = []

    for (id, title, content, time) in cursor.fetchall():
        list.append({"id": id, "title": title, "content": content, "time": time})

    return render_template('list.html', list=list, user=getCurrentlyLoggedInUser())


@app.route("/list", methods=["POST"])
def page_list_post():
    if request.form['delete'] != None:

        user = getCurrentlyLoggedInUser()
        if user['user_type'] != 1:
            flash(u"No privilege", 'error')
            return redirect('/list')

        cursor = dbConnection.cursor()
        cursor.execute('delete from post where id = %s', [request.form['delete']])

        flash(u"删除成功！", 'success')
        return redirect('/list')

    else:
        flash(u"action not supported", 'error')
        return redirect('/list')


@app.route("/item/<id>")
def page_item(id):
    post = get_post(id)
    return render_template("item.html", post=post, user=getCurrentlyLoggedInUser())


@app.route("/item/<id>", methods=["POST"])
def page_item_post(id):
    if request.form['action'] == 'delete':

        user = getCurrentlyLoggedInUser()
        if user['user_type'] != 1:
            flash(u"No privilege", 'error')
            return redirect('/item/' + id)

        cursor = dbConnection.cursor()
        cursor.execute('delete from post where id = %s', [id])

        flash(u"删除成功！", 'success')
        return redirect('/list')

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
    if request.form['password'] != request.form['password-repeat']:
        flash(u"两次密码不一致", 'error')
        return redirect('/auth/register')

    # 判断是否用户名已经存在
    # query判断
    # flash(u"用户已经存在！！", 'error')

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
