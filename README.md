#说明
本教程是给完全没有使用经验的Flask新手看，有基础的同学可以略过。原理并不是讲得很透彻，也不是最佳实践，很多代码甚至写得比较丑陋。但本教程的目的是：让使用者一个bare minimum的新知识，并在这些新知识的基础上比较快速地用Python开发出一个网站。

本教程包含：

1.  安装
2.  PyCharm使用、Workflow Tips
3.  后端路由、模板引擎
4.  数据库的读写
5.  用户注册与登入、鉴权
6.  用户输入信息的处理、业务逻辑
7.  CSS美化界面（略）

以上是概念部分
还包含一个非常简单的“论坛”：
允许用户注册、登入、发帖、允许管理员删帖。

论坛就在这个Git Repository中，SQL数据库在database.sql中。

第一次Commit（First commit）只涉及到本教学中的概念，后面对代码进行了一些重构，加入了中间件等（用来登入用户）。建议一个个Commit看。根据个人接受能力，可以选择理解/照抄/忽略第一次Commit之后的代码。

预计学习时间为4小时。


#安装
1. Python 2.7
   确定python --version中显示的版本为2.7

2. pip install flask

检查Path环境变量是否包括Python目录
[没有安装PIP？下载地址](http://python-packaging-user-guide.readthedocs.io/en/latest/installing/#install-pip-setuptools-and-wheel)

#RTFM
[**Flask** http://flask.pocoo.org/docs/0.10/](http://jinja.pocoo.org/docs/)

[**Jinja2 (template engine)** http://jinja.pocoo.org/docs/](http://jinja.pocoo.org/docs/)

[**Python Database API Specification v2.0 (PEP 249)** http://www.python.org/dev/peps/pep-0249/](http://www.python.org/dev/peps/pep-0249/)

# 用PyCharm新建Flask工程
记得Python Interpreter选2.7的
快捷键```Shift+F10```运行程序
按```Ctrl+F5```重新运行。

默认情况下，每做一次修改，都需要按```Ctrl+F5```重新运行。

但可以使用DebugMode，让它自动重新运行。
http://flask.pocoo.org/docs/0.10/quickstart/#debug-mode
运行后看到
	 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
在浏览器中打开 http://127.0.0.1:5000/ 访问

PyCharm有用的快捷键：
Alt+Enter自动纠正错误（光标在黄底字上时）
Ctrl+Shift+N跳到另一个文件
Ctrl+Tab跳到之前的文件
Ctrl+Shift+空格自动补全
Alt+J多重光标
Ctrl+P函数参数提示
Ctrl+B转到定义

## 禁用缓存
如果代码改了(尤其是JS、CSS)、刷新了浏览器，但结果没变，很可能是缓存的问题。
[Chrome禁用所有缓存的方法](http://stackoverflow.com/questions/5690269/disabling-chrome-cache-for-website-development)

## Flask starter
    from flask import Flask

    app = Flask(__name__)


    @app.route('/')
    def hello_world():
        return 'Hello World!'


    if __name__ == '__main__':
        app.run(debug=True)

## 目录结构
    | PJ.py 		//主程序
    ├─static		//静态资源，如图片、CSS、JS等
    └─templates	 //Jinja模板引擎中用到的模板

## Flask中适用的print调试法
	import json
	...
    
    @app.route('..')
    def func():
    	
        ...
		return json.dumps(object)
		...
        
object就算是一个很复杂的对象也可以一次性打出所有信息。
当然用PyCharm的调试功能也OK

## import
在程序的第一行，往往会有

	from flask import Flask, render_template, session, request, redirect, flash

这种代码。这是从Flask中导入各种对象。如果出现：

    NameError
    NameError: global name 'xxx' is not defined

往往是因为没有import。PyCharm会在下面画红波浪线提醒

## UTF-8支持
如果中文出现乱码，在第一行中添加
	# coding=utf-8

中文的string还要加个u，来显示表明后面的string是UTF-8

	u'添加成功！标题是' + request.form['title']

# 后端路由、模板引擎
##文档地址
http://flask.pocoo.org/docs/0.10/quickstart/#routing
##路由(router)的概念
简单理解为：声明每当用户访问某网址(如/list)时，要触发什么程序（函数）。

	@app.route('/')
    def index():
        return 'Hello World!'

路由由两部分组成：
1. @app.route标注
2. 回调函数(index())

具体原理不必深究，会用即可
从上面的代码可以很明显地看出，当用户访问'/'时，显示（返回）Hello World!
注：要把HTML打印到浏览器上（作为一个Response传送给浏览器），要用return，而不是print

PJ推荐简单粗暴的写法：每一个页面写一个router,直接在回调函数中完成所有的业务逻辑。
虽然不优雅，但是简单。

    @app.route('/')
    def page_index():
        return 'Hello World!'


    @app.route('/list')
    def page_list():
        return 'Showing the list!'


    @app.route('/new')
    def page_new():
        return 'add new item to the list!'

就这样，多添加一些路由。

##模板引擎

http://flask.pocoo.org/docs/0.10/quickstart/#rendering-templates

直接return内联string，非常没有表现力，把整个网页的HTML（几百行）都放到return里？代码会杂乱不堪。模板引擎就是为了解决这个问题。

###模板引擎的构成

####1.一套模板语言

        <!doctype html>
        <title>Hello from Flask</title>
        {% if name %}
          <h1>Hello {{ name }}!</h1>
        {% else %}
          <h1>Hello World!</h1>
        {% endif %}


是HTML语言的拓展，标准HTML语言之外，还多了```{{ varName }}```和```{% directive %}```.

HTML语言？是一棵树（由<directive></directive>嵌套而成的树），定义了网页的**结构与内容**。


####2.渲染模板的API

PJ简单粗暴，只要掌握这一个API即可（注意要先import）

	from flask import render_template

    def xxx():
        return render_template('mytemplate.html')

这个API会读取```templates/mytemplate.html```并渲染它（返回的是一个string，渲染结果HTML）

还可以传参数哦，如

    return render_template('welcome.html', name="Kevin", greeting="Welcome")

在模板里写

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
        {{ greeting }}, {{ name }}!
    </body>
    </html>


```{{ varName }}```会被替换掉的。所以会显示成

	Welcome, Kevin!

#####{% directive %}
这也非常有用，在PJ中要掌握：

if

    {% if(condition) %}
    {% else %}
    {% endif %}

for

    {% for item in list %}
 		{{ item }}
    {% endfor %}

写个综合的：

模板：

    <ol>
        {% for item in list %}
            {% if(not item.hidden) %}
                <li>
                    <h1>          {{ item.title }}</h1>
                    <p>
                        {{ item.content }}
                    </p>
                </li>
            {% endif %}
        {% endfor %}
    </ol>

渲染：

	return render_template('list.html',
                                   list=[
                                       {"title": "123", "content": "aaa", "hidden": 0},
                                       {"title": "abc", "content": "aaaaaa", "hidden": 0},
                                       {"title": "asd", "content": "aaawwww", "hidden": 0},
                                       {"title": "hidden", "content": "aaawwww", "hidden": 1}
                                   ])

仔细看，应该不难懂。
PS如果看不懂list=后面的语法，查一下[JSON](http://www.w3schools.com/json/)。大致就是:[]表示数组，{"key":value}表示键值对（数据库查询结果基本也是这种）

还需要掌握**模板继承**
http://flask.pocoo.org/docs/0.10/patterns/templateinheritance/#template-inheritance
想象一个页面90%的内容都是一样的（如header、footer版权信息、css…）只有10%的内容会改变。模板继承允许所有的网页继承自一个模板，只改需要修改的内容。重要性不言而喻。

用```{% block %}```这条指令实现模板继承。
实例：

编写layout.html（相当于主模板）

    <!doctype html>
    <html>
      <head>
        {% block head %}
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <title>{% block title %}{% endblock %} - My Webpage</title>
        {% endblock %}
      </head>
      <body>
        <div id="content">{% block content %}{% endblock %}</div>
        <div id="footer">
          {% block footer %}
          &copy; Copyright 2010 by <a href="http://domain.invalid/">you</a>.
          {% endblock %}
        </div>
      </body>
    </html>

主模板中定义了```head```、```title```和```footer```三个可以被替换的块

编写child1.html自模板，让它集成自layout.html

    {% extends "layout.html" %}
    {% block title %}Index{% endblock %}
    {% block head %}
      {{ super() }}
      <style type="text/css">
        .important { color: #336699; }
      </style>
    {% endblock %}
    {% block content %}
      <h1>Index</h1>
      <p class="important">
        Welcome on my awesome homepage.
    {% endblock %}

替换了这三个块。
注：```super()```表示父模板中该块的内容。
能猜出

	return render_template('child1.html')

的执行结果了吧

# 数据库的读写

Python数据库API都是满足这个规范的：
http://www.python.org/dev/peps/pep-0249/
所以Informix和Mysql之间迁移应该不难实现。

鉴于Informix每次开启都要卡10秒钟，很影响开发心情，可以搭一个本地的MySQL，做完后再改成远端的Informix。

##Informix 演示

    import jaydebeapi

    conn = jaydebeapi.connect('com.informix.jdbc.IfxDriver',
                              'jdbc:informix-sqli://crl.ptopenlab.com:9088/***:INFORMIXSERVER=ifxserver1;USER=***;PASSWORD=***;DB_LOCALE=en_us.utf8',
                              'E:\\PythonProjects\\ifxjdbc.jar', )

    curs = conn.cursor()

    curs.execute("select * from weather_station")

    for row in curs.fetchall():
        for col in row:
            print col
        print "\n"

##MySQL 演示
Connector安装：http://dev.mysql.com/downloads/connector/python/
32位/64位要根据自己装的python选择，选Python 2.7的

    import datetime
    import mysql.connector

    cnx = mysql.connector.connect(user='scott', database='employees')
    cursor = cnx.cursor()

    query = ("SELECT first_name, last_name, hire_date FROM employees "
             "WHERE hire_date BETWEEN %s AND %s")

    hire_start = datetime.date(1999, 1, 1)
    hire_end = datetime.date(1999, 12, 31)

    cursor.execute(query, (hire_start, hire_end))

    for (first_name, last_name, hire_date) in cursor:
      print("{}, {} was hired on {:%d %b %Y}".format(
        last_name, first_name, hire_date))

    cursor.close()
    cnx.close()

1. 连接数据库
2. 获得cursor对象
3. 执行execute
4. 读取结果
5. 关闭cursor和connection (不关也没事)

是不是超级简单。。依样画葫芦就行了。
不管是查询数据（SELECT）还是添加/删除（INSERT/DELETE），都用```.execute()```方法。

##两个新概念：
###cursor
一次数据库查询（广义）操作的上下文，可用来执行查询、读取数据等。

用cursor执行query、读取全部数据，只要调用

	cursor.execute(query, bindings)

有两种方法读取execute的结果。
第一种：迭代cursor（必须这样做，直接print cursor得不到结果，这是python特有的迭代器）

    for (first_name, last_name, hire_date) in cursor:
      print("{}, {} was hired on {:%d %b %Y}".format(
        last_name, first_name, hire_date))

用for..in..这样子一行行地读取它

第二种：
	
    print cursor.fetchall()

.fetchall会把所有的结果取出，放到一个数组中。这个数组可以直接传到模板引擎的参数绑定中。


或者直接把它传到模板引擎的参数绑定中

###参数绑定
书上应该也有提过，用来防SQL注入、提高效率的。


    query = ("SELECT first_name, last_name, hire_date FROM employees "
             "WHERE hire_date BETWEEN %s AND %s")

    hire_start = datetime.date(1999, 1, 1)
    hire_end = datetime.date(1999, 12, 31)

    cursor.execute(query, [hire_start, hire_end])


execute的第二个参数是个数组，这个数组会被绑定到query中，按照顺序替换每一个%s
注意：这里即使是数字，也不要写%d,不管什么，只要是参数就写%s

# 用户注册与登入、鉴权
##HTTP协议
###请求(request)和响应(response)
HTTP分请求和反馈两个部分。
请求是指用户发送给服务器的数据，
响应是指服务器发送给用户的数据。
###无状态
HTTP是一个```无状态```的协议，就是说，每次请求都与上次是无关的。（不像普通程序，需要在内存中存储当前状态）

##使用Session登入
因为HTTP是无状态的，所以为了确定用户标识，必须依靠一个叫做Session(会话)的东西。会话其实很简单：每个用户第一次访问网站，都会被赋予一个SessionID,这个SessionID是唯一的，用来确认用户本次访问的身份（相当于HTTP无状态的一个补偿，用过ID，人工确定其状态）。用户在访问网站的过程中，每次访问一个网页，都要（在请求中）把SessionID告诉服务器。服务器通过SessionID就可以查询到用户的身份了。
SessionID具体是怎么做的呢？是通过Cookie传给浏览器的，浏览器再读Cookie发给服务器。HTTP协议规定，访问一个域名时，必须把该域名下所有的Cookie发送给服务器（如访问http://www.baidu.com/就要把百度留下的Cookie发回去）这种机制就确保了服务器能通过SessionID确定用户身份（了解即可）

####TL;DR version
在Python中使用Session就可以做到登入了!
但是使用Session之前，要先设置个Flask用于加密Session的密码
	
    app.secret_key = '123456'

设置好了，直接看代码吧：


    def get_user(user_id):
        if (user_id == None): return None
        cursor = dbConnection.cursor()
        cursor.execute('select id,name,password from `user` where id=%s', [user_id])
        result = cursor.fetchall()
        if len(result) == 0:
            return None
        else:
            user = result[0]
            return {"id": user[0], "name": user[1], "password": user[2]}


    @app.route('/simulate-login')
    def page_simulate_login():
        session['user_id'] = 1
        return redirect('/')


    @app.route('/simulate-logout')
    def page_simulate_logout():
        del session['user_id']
        return redirect('/')


    @app.route('/')
    def page_index():
        return render_template('welcome.html', user=get_user(session.get('user_id', None)))

##鉴权
鉴权（Authorization）是判断用户是否有权限执行某操作的过程。比如要删除一个帖子，只有管理员才有权限。最简单的鉴权其实非常容易，只要在数据库中加一个user_type，0表示普通用户，1表示管理员。然后在删除帖子时判断下(用之前写的get_user helper函数获得user_type)，没有权限弹出一个错误阻止继续进行就行了。（怎么抛出错误在业务逻辑中说）

PJ中也只要用这种最简单的鉴权就够了


# 用户输入信息的处理、业务逻辑
业务逻辑是处理用户输入到查询数据库到做出一系列判断到更新数据库到返回给用户信息这个过程中逻辑的统称。
用户输入信息的处理，即Request的处理，PJ中大概要用到两种：
##1.URL中的信息（如：查看文章详情 /page/5）
URL中的信息也是Request中的输入信息，虽然这个信息不会是用户手工输入的（而是点击链接得到的）
HTTP有两种动词：```GET```和```POST```这种是属于GET，参数在url中，处理方法很简单：在路由中定义一个模板

    @app.route('/page/<id>')
    def page_page(id):    
        return render_template('page.html', page=get_page(id)

Flask非常聪明，在url中以尖括号括起来的，会捕获并当成参数传给回调函数

##2.表单中的信息
如果用户要输入某些东西并提交（比如发个帖子），表单提交，一般是使用```POST```的HTTP请求(如果要传输数据，非常不建议GET)。看一个表单：

Python代码：

    @app.route('/form')
    def page_form():
        return render_template('form.html')

form.html：

    {% extends "base.html" %}
    {% block body %}
        <form action="" method="POST">
            <div>
                标题：<input type="text" name="title"/>
            </div>
            <div>
                内容：<textarea name="content" id="" cols="30" rows="10">
                </textarea>
            </div>
            <div>
                <button type="submit">
                    Submit
                </button>
            </div>
        </form>
    {% endblock %}

这个表单位于/form，```action```指定的是表单的目标（跳转到哪个网页）,""代表还是该url(即/form)，但是method="POST"指定了跳转后，会以POST形式请求。（浏览器一般是以GET方式请求的）。

在input和textarea等可以由用户输入的控件中，要把name设置一下，这将是Python处理用户输入数据时的key。

表单做好之后，我们要设置个专门处理POST请求的路由（@app.route默认是只处理GET不处理POST的），在这个路由中我们要获得用户之前输入的数据。获得表单中的变量也很方便：用request.form['key']即可

    @app.route('/form', methods=['POST'])
    def page_form_post():
        return json.dumps(request.form)

上面这个会打出所有的用户输入

##显示成功/错误信息
http://flask.pocoo.org/docs/0.10/quickstart/#message-flashing
成功/错误信息一般不会直接在POST路由中打出。而是被暂存在Session中。POST路由业务逻辑执行完后，往往是把用户redirect到另一个页面。在那个页面，检查Session中有没有该消息。有的话则打出并删除那个消息。这种机制叫做Flashing

Flask有很好的Flashing支持。修改之前写的代码

在base.html中添加

    {% with errors = get_flashed_messages(category_filter=["error"]) %}
        {% if errors %}
            <div class="error">
            <ul>
                {%- for msg in errors %}
                    <li>{{ msg }}</li>
                {% endfor -%}
            </ul>
        {% endif %}
    {% endwith %}

    {% with succesess = get_flashed_messages(category_filter=["success"]) %}
        {% if succesess %}
            <div class="success">
            <ul>
                {%- for msg in succesess %}
                    <li>{{ msg }}</li>
                {% endfor -%}
            </ul>
        {% endif %}
    {% endwith %}


（更好的方法是 ```{% include 'error_messages.html' %}``` ```{% include 'success_messages.html' %}```）

在Python代码中添加Flash Message的部分

    @app.route('/form', methods=['POST'])
    def page_form_post():
        if (len(request.form['title']) < 5):
            flash(u'标题太短了！', 'error')
            return redirect('/form')

        flash(u'添加成功！标题是' + request.form['title'], 'success')
        return redirect('/form')


# CSS美化界面

##通过CSS做样式
两种写CSS的方法：
###1.内联CSS
如：

	<p style="color:red;font-size:20px"></p>

###2.通过class
如：
	
    <p class="title">ABC</p>

并添加一个.css文件styles.css 在<head>..</head>里添加

	<link rel="stylesheet" href="styles.css">
    
CSS教程

* http://www.w3schools.com/css/

##Bootstrap

先引入Bootstrap的CSS

	<link rel="stylesheet" href="//cdn.bootcss.com/bootstrap/4.0.0-alpha.2/css/bootstrap.css">


Bootstrap内部做了很多class。加上去立刻好看很多。

如

	<button type="submit" class="btn btn-default">Submit</button>

和

    <form class="form-horizontal">
      <div class="form-group">
        <label class="col-sm-2 control-label">Email</label>
        <div class="col-sm-10">
          <p class="form-control-static">email@example.com</p>
        </div>
      </div>
      <div class="form-group">
        <label for="inputPassword" class="col-sm-2 control-label">Password</label>
        <div class="col-sm-10">
          <input type="password" class="form-control" id="inputPassword" placeholder="Password">
        </div>
      </div>
    </form>

Bootstrap的栅格系统也是排版利器。还是读文档吧：
http://getbootstrap.com/css/#forms-controls-static

Bootstrap教程
* http://www.w3schools.com/bootstrap/

