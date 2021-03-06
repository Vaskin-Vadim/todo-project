import code
from distutils.debug import DEBUG
import time
import json
from datetime import datetime
from flask import Flask, request,  render_template,redirect,session,url_for,jsonify,send_file,flash
from flask import Flask,render_template,request
from flask_migrate import Migrate
from sqlalchemy import false
from models import db, User
from models import login
from flask_login import login_required,current_user, login_user,logout_user
from io import BytesIO
import psycopg2 #pip install psycopg2 
import psycopg2.extras
from flask_socketio import SocketIO
import requests
from flask_mail import Mail, Message
import random

# num = input('login ')
# pas = ''
# for x in range(16): #Количество символов (16)
#     pas = pas + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ')) #Символы, из которых будет составлен пароль
# print('Hello, ', num, 'your password is: ', pas)

def sent_to(text):
    token = "5515854359:AAHA8Mdqxr5ACLPWPwicUqL88gvbZrJcB-c"
    chat_id = "-673828552"
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
    results = requests.get(url_req)
    print(results.json())


MAX_FILE_SIZE = 1024 * 1024 + 1

app = Flask(__name__)


POSTGRES = {
    'user': 'postgres',
    'pw': 'nigerdyai',
    'db': 'flask',
    'host': 'todo-db',
    'port': '5432',
}


DB_HOST = "todo-db"
DB_NAME = "flask"
DB_USER = "postgres"
DB_PASS = "nigerdyai"






messages_file = "./data/messages.json"
json_file = open(messages_file, "rb")
data = json.load(json_file)
if not "all_messages" in data:
    print(f"ERROR1")
    exit(1)
app.config.update(
                DEBUG=True,
                MAIL_SERVER = "smtp.yandex.ru",
                MAIL_PORT = 465,
                MAIL_USE_SSL= True,
                MAIL_USERNAME = "todo.application@yandex.ru",
                MAIL_PASSWORD = 'NigerdyaiV4K'
)
mail = Mail(app)

@app.route("/send_email")
def send_mail(message,kuda):
   msg = Message(
                'About dashboard',
                sender = 'todo.application@yandex.ru',
                recipients = [kuda]
               )
   msg.body = message
   mail.send(msg)
   



@app.route("/check",methods=["GET", "POST"])
def check_mail():
    if request.method == 'POST':
        email = request.form.get("email")
        pas = ''
        for x in range(16): #Количество символов (16)
            pas = pas + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ')) #Символы, из которых будет составлен пароль
            # pas='123456'
        send_mail(pas,email)
        new_code = Email(code=pas,email=email)
        db.session.add(new_code)
        db.session.commit()
        flash('На ваш адрес электронной почты был отправлен код подтверждения')
        return render_template("registr1.html",pas=pas,email=email)




all_messages = data["all_messages"]

def save_messages():
    data = {
        "all_messages": all_messages
    }
    json_file = open(messages_file, "w")
    json.dump(data, json_file)

def time_format(t):
   now =  time.strftime("%H.%M.%S", time.localtime())
   return str(now)

#вот сюда сделать запрос базы данных постгрес, есть исходники у женька
socketio = SocketIO(app)

@app.route("/")
def chat():
    return redirect('log')

@app.route("/get_messages")  #ЗАПРОС НА ЧТЕНИЕ ДАННЫХ
def get_messages():
    return {"messages": all_messages}


         
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

@app.route('/test')
def index2():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM usernames")
    topphpframework = cur.fetchall() 
    return render_template('new.html', topphpframework=topphpframework)

@app.route("/ajax",methods=["POST","GET"])
def ajax():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        getid = request.form['id']
        getname = request.form['name']
        if getname.isspace():
            return jsonify('Record updated successfully')
        else:
            print(getid)
            cur.execute("UPDATE task SET title_task = %s WHERE id = %s ", [getname, getid])
            conn.commit()       
            cur.close()
            return jsonify('Record updated successfully')

@app.route("/ajax1",methods=["POST","GET"])
def ajax1():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        getid = request.form['id']
        getname = request.form['name']
        print(getid)
        cur.execute("UPDATE todo SET title = %s WHERE id = %s ", [getname, getid])
        conn.commit()       
        cur.close()
    return jsonify('Record updated successfully')


@app.route("/update_todo",methods=["POST","GET"])
def update_todo():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        getitle = request.form['title']
        getdescription = request.form['description']
        getid = request.form['id_task']
        dash_id = request.form.get("dash")
        cur.execute("UPDATE todo SET title = %s WHERE id = %s ", [getitle, getid])
        cur.execute("UPDATE todo SET description = %s WHERE id = %s ", [getdescription, getid])
        conn.commit()       
        cur.close()
        return redirect(url_for('show',dash_id=dash_id,todo_id=getid))





@app.route("/update_user",methods=["POST","GET"])
def update_user():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        first_name = current_user.name
        gename = request.form['name']
        getemail = request.form['email']
        getid = request.form['id_user']
        dash_id = request.form['dash']
        
        cur.execute("UPDATE usernames SET name = %s WHERE id = %s ", [gename, getid])
        cur.execute("UPDATE usernames SET email = %s WHERE id = %s ", [getemail, getid])

        name = User.query.filter_by(name=first_name).first()
        if name:
            print(name)
            print(first_name)
            print(gename)
            
            
            cur.execute("UPDATE roles SET name = %s WHERE id_person = %s ", [gename, getid])
            cur.execute("UPDATE roles__dash SET name = %s WHERE id_person = %s ", [gename, getid])
            cur.execute("UPDATE chat SET name = %s WHERE name = %s ", [gename, first_name])
            conn.commit()       
            cur.close()

        conn.commit()       
        cur.close()
        return redirect(url_for("home",dash_id=dash_id))

@app.route("/update_time",methods=["POST","GET"])
def update_time():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        gethours = request.form['hour']
        getminutes = request.form['minute']
        getid = request.form['task_id']
        dash_id = request.form['dash']
        getide = request.form['todo_id']
        cur.execute("UPDATE task SET hours = %s WHERE id = %s ", [gethours, getid])
        cur.execute("UPDATE task SET minutes = %s WHERE id = %s ", [getminutes, getid])



        conn.commit()       
        cur.close()
        return redirect(url_for('show',dash_id=dash_id,todo_id=getide))













@app.route("/ajax2",methods=["POST","GET"])
def ajax2():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        getid = request.form['id']
        getname = request.form['name']
        print(getid)
        cur.execute("UPDATE todo SET description = %s WHERE id = %s ", [getname, getid])
        conn.commit()       
        cur.close()
    return jsonify('Record updated successfully')

@app.route("/ajax3",methods=["POST","GET"])
def ajax3():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        getid = request.form['id']
        getname = request.form['name']
        if getname.isspace():
            return jsonify('Record updated successfully')
        else:
            print(getid)
            cur.execute("UPDATE chat SET message = %s WHERE id = %s ", [getname, getid])
            conn.commit()       
            cur.close()
            return jsonify('Record updated successfully')


@app.route("/ajax4",methods=["POST","GET"])
def ajax4():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        getid = request.form['id']
        getname = request.form['name']
        if getname.isspace():
            return jsonify('Record updated successfully')
        else:
            print(getid)
            cur.execute("UPDATE dashboards SET dash = %s WHERE id = %s ", [getname, getid])
            conn.commit()       
            cur.close()
            return jsonify('Record updated successfully')





@app.route("/todo_status",methods=["POST","GET"])
def todo_status():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':    
        
        todo_id = request.form.get("todo_id")
        activate = request.form.get("activate")
        status = request.form.get("todo_status")
        cur.execute("UPDATE todo SET activate = %s WHERE id = %s ", [activate, todo_id])
        cur.execute("UPDATE todo SET status = %s WHERE id = %s ", [status, todo_id])
        conn.commit()       
        cur.close()
    return redirect(url_for("home"))



@app.route("/<int:dash_id>/show/<int:todo_id>")
def show(dash_id,todo_id):
    dash = Dashboards.query.filter_by(id=dash_id).first()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM task")
    topphpframework = cur.fetchall() 
    todo = Todo.query.filter_by(id=todo_id).first()
    todo1 = Todo.query.filter_by(id=todo_id).first()
    # task_list = Task.query.all()
    todo_list = Todo.query.all()
    role_list = User.query.all()
    role_list_u = Roles.query.all()
    current = current_user.name
    current_id = current_user.id
    current_status = current_user.status
    wet = Roles.query.filter_by(name=current,id_task=todo.id).first()
    if wet:
        g='yes'
    else:
        g='no'

    admin = "admin"    
    todo3 = Task.query.all()
    sum1 = 0
    for i in todo3:
        if i.id_task == todo_id:
            sum1 += i.hours
    sum2 = 0
    for i in todo3:
       if i.id_task == todo_id: 
        sum2 += i.minutes
    sum3 = sum2//60
    sum4 = sum3 + sum1
    sum5 = sum2-60*sum3
    task_list = Task.query.all()
    all = 0
    uns = 0
    for i in task_list:
        if i.id_task == todo_id:
            all=all+1
            if i.complete == 1:
                uns = uns + 1
    for i in todo_list:
        if todo.status == '0': todo_status = "без статуса"
        if todo.status == '1': todo_status = "не начато"
        if todo.status == '2': todo_status = "в процессе"
        if todo.status == '3': todo_status = "выполнено"

    
    return render_template("post_detail.html",dash=dash,current_status=current_status,current_id=current_id,current=current,admin=admin,g=g,todo=todo,todo1=todo1,role_list=role_list,role_list_u=role_list_u,topphpframework=topphpframework,sum4=sum4,sum5=sum5, all =all,uns=uns,todo_status=todo_status )



# @app.route("/show/<int:todo_id>")
# def show(todo_id):
#     todo = Todo.query.filter_by(id=todo_id).first()
#     task_list = Task.query.all()
#     role_list = User.query.all()
#     role_list_u = Roles.query.all()
#     current = current_user.name
#     admin = "admin"    
#     return render_template("post_detail.html",current=current,admin=admin, todo=todo,task_list=task_list,role_list=role_list,role_list_u=role_list_u)





app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db.init_app(app)

################################################################



login.init_app(app)
login.login_view = 'login'
app.secret_key = 'xyz'

@app.before_first_request
def create_all():
    db.create_all()

# @app.route('/chat')
# @login_required
# def chat2():
#     return render_template('chat.html')



global name_check 
@app.route('/log', methods = ['POST', 'GET'])
def login():    
    if request.method == 'POST':  
        email = request.form['email']
        user = User.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            global name_check   
            name_check= email
            return redirect(url_for('home1'))
        else:
            flash('Неверное имя пользователя или пароль')
    return render_template('log.html')



######################################################################################
@app.route("/registr1", methods=["GET", "POST"])
def index():
    if request.method == 'POST':  # When a user clicks submit button it will come here.
        data = request.form  # request the data from the form in index.html file
        name = data["name"]
        email = data["email"]
        pas = data["pas"]
        code = data["code"] 
        print(pas)
        print(code)        
        status = data["secret"]
        check = Admin.query.filter_by(code=status).first()   
        password_hash = data["password"]
        created_on = datetime.utcnow()
        updated_on = datetime.utcnow()
        user = User.query.filter_by(email=email).first()   
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email уже используется')
            return render_template("registr1.html")
        if check:
            status = 'admin'
        else:
            status = 'viewer'
        email_norm = Email.query.filter_by(code=code).first()
        if email_norm:
            email=email_norm.email
            new_data = User(name, email, password_hash,created_on,updated_on,status)
            Email.query.filter_by(email=email).delete()
            db.session.add(new_data)
            db.session.commit()
            print('Hello')
            user_data = User.query.all()
        #print(user_data)
            return redirect('log')
        else:
            flash('Неправильно введён код подтверждения почты')
            return render_template("registr1.html")
    return render_template("registr1.html")

@app.route("/usersdata")
@login_required
def usersdata():

    return render_template("usersdata.html" ,  user_data = User.query.all())
@app.route("/send") # ЗАПРОС НА ИЗМЕНЕНИЕ ДАННЫХ
@login_required
def send_message():
    text = request.args["text"]
    #name = request.args["name"]

    # if len(name) > 10 or len(name) < 2:
    #     return "ERROR"
    # if len(text) > 3000 or len(name) < 1:
    #     return "ERROR"

    message ={
        "text": text,
        "name": current_user.name,
        "time": time.strftime("%H:%M:%S", time.localtime()),
        "name_check": current_user.name
    }
    all_messages.append(message)
    save_messages()
    return "OK"

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    message = db.Column(db.String(400))   
    time = db.Column(db.DateTime(), default=datetime.utcnow)
    id_chat = db.Column(db.Integer)
    id_person = db.Column(db.Integer)
    

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8))
   
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(150))
    email = db.Column(db.String(150))
    

class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    id_task = db.Column(db.Integer)
    id_person = db.Column(db.Integer)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    time = db.Column(db.String(200))
    
class Dashboards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dash = db.Column(db.String(200))

class Org(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(400))
    


@app.route("/dashboards")
@login_required
def home1():
    dash_list = Dashboards.query.all()
    sotr_list = Roles_Dash.query.all()
    role_list = User.query.all()
    current_name=current_user.name
    current_status=current_user.status
    chis = Dashboards.query.count()
    todo = Todo.query.count()
    sotr = User.query.count()
    task = Task.query.count()
    he=''
    admin='admin'
    return render_template("dashboards.html",current_status=current_status,admin=admin,chis=chis,current_name=current_name,role_list=role_list,sotr_list=sotr_list,dash_list=dash_list, todo= todo,sotr =sotr,task=task)

@app.route("/add_dash", methods=["POST"])
@login_required
def add_dash():
    title = request.form.get("title")
    new_dash = Dashboards(dash=title)
    db.session.add(new_dash)
    db.session.commit()
    user_email = User.query.all()
    description = 'Администратором была добавлена новая доска'
    for j in user_email:
        email=j.email
        send_mail(description,email)
    return redirect(url_for("home1"))


@app.route("/show_dash/<int:dash_id>")
def home(dash_id):
    dash = Dashboards.query.filter_by(id=dash_id).first()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM history ORDER BY id DESC")
    history_list = cur.fetchall() 
    todo_list = Todo.query.filter_by(dash_id=dash_id).all()
    current = current_user.name
    user_email = current_user.email
    user_status = current_user.status
    user_id = current_user.id
    # user_gender = current_user.gender
    admin = "admin"    
    return render_template("base.html",user_id=user_id,user_status=user_status, todo_list=todo_list,current=current,admin=admin,user_email=user_email,history_list=history_list,dash=dash)



@app.route("/add_role", methods=["POST"])
@login_required
def add_role():
    name = request.form.get("name")    
    id_task = request.form.get("id_task")
    dash_id = request.form.get("dash")
    user_id = User.query.filter_by(name=name).first()    
    if user_id: # if a user is found, we want to redirect back to signup page so user can try again
        id_person = user_id.id

        user = Roles.query.filter_by(id_task=id_task,id_person=id_person).first()
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Сотрудник уже прикреплён к задаче')
            return redirect(url_for('show',dash_id=dash_id,todo_id=id_task))

        new_role = Roles(name=name,id_task=id_task,id_person=id_person)
        db.session.add(new_role)
        db.session.commit()
        description = request.form.get("history")
        time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
        new_description = History(description=description,time=time)
        db.session.add(new_description)
        db.session.commit()
        sent_to(description)
        user_todo = Roles.query.filter_by(id_task=id_task).all()
        user_email = User.query.all()
        for i in user_todo:
            for j in user_email:
                if (i.id_person == j.id):
                    email=j.email
                    send_mail(description,email)
        return redirect(url_for('show',dash_id=dash_id,todo_id=id_task))


    else:
        flash('Некорректный ввод данных (возможно пользователя не существует)')
        return redirect(url_for('show',dash_id=dash_id,todo_id=id_task))

class Roles_Dash(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    id_dash = db.Column(db.Integer)
    id_person = db.Column(db.Integer)

@app.route("/add_role_dash", methods=["POST"])
@login_required
def add_role_dash():
    name = request.form.get("name")
    name_dash = request.form.get("dash")    
    user_id = User.query.filter_by(name=name).first()    
    dash_id = Dashboards.query.filter_by(dash=name_dash).first()    
    if user_id: # if a user is found, we want to redirect back to signup page so user can try again
        id_person = user_id.id
        id_dash = dash_id.id
        user = Roles_Dash.query.filter_by(id_dash=id_dash,id_person=id_person).first()
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Сотрудник уже находится на этом проекте')
            return redirect(url_for('home1'))
        new_role = Roles_Dash(name=name,id_dash=id_dash,id_person=id_person)
        db.session.add(new_role)
        db.session.commit()
        return redirect(url_for('home1'))

    else:
        flash('Некорректный ввод данных (возможно пользователя не существует)')
        return redirect(url_for('home1'))










@app.route("/delete_role", methods=["POST"])
@login_required
def delete_role():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    name = request.form.get("name")    
    dash_id = request.form.get("dash")
    print(name)
    id_task = request.form.get("id_task")
    cur.execute("DELETE FROM roles  WHERE name = %s AND id_task = %s", [name, id_task])
    conn.commit()       
    cur.close()
    return redirect(url_for('show',dash_id=dash_id,todo_id=id_task))




@app.route("/update_org",methods=["POST","GET"])
def update_org():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        cur.execute("UPDATE todo SET title = %s WHERE id = %s ", [title, 1])
        cur.execute("UPDATE todo SET description = %s WHERE id = %s ", [description, 1])
        conn.commit()       
        cur.close()
        return redirect(url_for('home1'))


@app.route("/check_user", methods=["POST"])
@login_required
def check_user():
    name = current_user.name
    id_task = request.form.get("id_task")
    dash_id = request.form.get("dash")
    user = Roles.query.filter_by(name=name,id_task=id_task).first()   
    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('chat4',dash_id=dash_id,todo_id=id_task))    
    flash('Присоединитесь к проекту, чтобы просматривать чат')
    return redirect(url_for('show',dash_id=dash_id,todo_id=id_task))


@app.route("/check_dash_user", methods=["POST"])
@login_required
def check_dash_user():
    name = current_user.name
    dash_id = request.form.get("dash")
    user = Roles_Dash.query.filter_by(name=name,id_dash=dash_id).first()   
    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('home',dash_id=dash_id))    
    flash('У вас нет доступа к этой доске')
    return redirect(url_for('home1'))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(400))   
    status = db.Column(db.String(1))
    activate = db.Column(db.String(1))
    role = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    dash_id = db.Column(db.Integer)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_task = db.Column(db.String(100))
    id_task = db.Column(db.Integer)
    date_of_begin = db.Column(db.String(100))
    date_of_end = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    hours = db.Column(db.Integer)
    minutes = db.Column(db.Integer)



@app.route("/add_message", methods=['POST'])
@login_required
def add_message():
    name = current_user.name
    id_person = current_user.id
    message = request.form['message']
    title = request.form['todo_title']
    # print(title)
    time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
    id_chat = request.form['id_chat']
    if message.isspace() or message=='':
        return redirect(url_for('chat4',todo_id=id_chat))
    else:
        new_message = Chat(name=name,message=message,time=time,id_chat=id_chat, id_person=id_person)
        db.session.add(new_message)
        db.session.commit()
        # sent_to("Пользователь " + name + " Оставил одно новое сообщение по задаче " + title + ".")
        return redirect(url_for('chat4',todo_id=id_chat))



@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    title_task = request.form.get("title")
    id_task = request.form.get("id_task")
    dash_id = request.form.get("dash")
    date_of_begin = request.form.get("date_of_begin")
    date_of_end = request.form.get("date_of_end")
    hours = '0'
    minutes = '0'
    new_task = Task(title_task=title_task,id_task=id_task,date_of_end=date_of_end,date_of_begin=date_of_begin, complete=False, hours=hours,minutes=minutes)
    db.session.add(new_task)
    db.session.commit()
    description = request.form.get("history")
    time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    new_description = History(description=description,time=time)
    db.session.add(new_description)
    db.session.commit()
    sent_to(description)
    user_todo = Roles.query.filter_by(id_task=id_task).all()
    user_email = User.query.all()
    for i in user_todo:
        for j in user_email:
            if (i.id_person == j.id):
                email=j.email
                send_mail(description,email)
    return redirect(url_for('show',dash_id=dash_id,todo_id=id_task))
    



# @app.route("/todo")
# @login_required


@app.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form.get("title")
    description = request.form.get("description")
    dash_id = request.form.get("dash")
    status = request.form.get("status")
    activate = request.form.get("activate")
    new_todo = Todo(title=title,description=description, complete=False,status=status,activate=activate,dash_id=dash_id)
    db.session.add(new_todo)
    db.session.commit()
    description = request.form.get("history")
    time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    new_description = History(description=description,time=time)
    db.session.add(new_description)
    db.session.commit()
    sent_to(description)
    user_todo = Roles_Dash.query.filter_by(id_dash=dash_id).all()
    user_email = User.query.all()
    for i in user_todo:
        for j in user_email:
            if (i.id_person == j.id):
                email=j.email
                send_mail(description,email)
    return redirect(url_for('home',dash_id=dash_id))




@app.route("/<int:dash_id>/chat/<int:todo_id>")
@login_required
def chat4(dash_id,todo_id):
    dash = Dashboards.query.filter_by(id=dash_id).first()
    todo = Todo.query.filter_by(id=todo_id).first()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM chat ORDER BY time ASC")
    mess_list = cur.fetchall() 
    up_list = Upload.query.all()
    current = current_user.name
    user_id = current_user.id
    
    return render_template("chat.html",dash=dash,user_id=user_id,current=current, todo=todo,mess_list=mess_list,up_list=up_list)

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

# @app.route("/update/<int:todo_id>")
# def update(todo_id):
#     todo = Todo.query.filter_by(id=todo_id).first()
#     todo.complete = not todo.complete
#     db.session.commit()
#     return redirect(url_for("home"))

@app.route("/<int:dash_id>/update_task/<int:task_id>")
@login_required
def update_task(dash_id,task_id):
    current = current_user.name
    task = Task.query.filter_by(id=task_id).first()
    task_t=task.title_task
    task.complete = not task.complete
    db.session.commit()
    sent_to("Пользователь " + current + " обновил статус  " + task_t + ".")
    return redirect(url_for('show',dash_id=dash_id,todo_id=task.id_task))


@app.route("/<int:dash_id>/delete/<int:todo_id>")
@login_required
def delete(dash_id,todo_id):
    if (todo_id==''):
        return redirect(url_for('home',dash_id=dash_id))
    else:
        todo = Todo.query.filter_by(id=todo_id).first()
        current = current_user.name
        db.session.delete(todo)
        db.session.commit()
        todo_t=todo.title
        sent_to("Администратор " + current + " удалил todo " + todo_t + ".")
        return redirect(url_for('home',dash_id=dash_id))

@app.route("/delete_dashboard/<int:dash_id>")
@login_required
def delete_dash(dash_id):
    todo = Dashboards.query.filter_by(id=dash_id).first()
    current = current_user.name
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('home1'))



@app.route("/<int:dash_id>/delete_task/<int:task_id>")
@login_required
def delete_task(dash_id,task_id):
    task = Task.query.filter_by(id=task_id).first()
    current = current_user.name
    task_t=task.title_task
    db.session.delete(task)
    db.session.commit()
    sent_to("Администратор " + current + " удалил подзадачу  " + task_t + ".")
    return redirect(url_for('show',dash_id=dash_id,todo_id=task.id_task))



#######################################################


class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)
    id_chat = db.Column(db.Integer)
    time = db.Column(db.DateTime(), default=datetime.utcnow)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upl():
    id_chat = request.form.get("id_chat")
    if request.method == 'POST':
        file = request.files['file']
        time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
        id_chat = request.form.get("id_chat")   
        dash_id = request.form.get("dash")   
        upload = Upload(filename=file.filename, data=file.read(),id_chat=id_chat,time=time)
        db.session.add(upload)
        db.session.commit()
        description = request.form.get("history")
        time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
        new_description = History(description=description,time=time)
        db.session.add(new_description)
        db.session.commit()
        sent_to(description)
        user_todo = Roles.query.filter_by(id_task=id_chat).all()
        user_email = User.query.all()
        for i in user_todo:
            for j in user_email:
                if (i.id_person == j.id):
                    email=j.email
                    send_mail(description,email)
        return redirect(url_for('chat4',dash_id=dash_id,todo_id=id_chat))
    return redirect(url_for('chat4',dash_id=dash_id,todo_id=id_chat))

@app.route('/download/<upload_id>')
@login_required
def download(upload_id):
    upload = Upload.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.data), attachment_filename=upload.filename, as_attachment=True)





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/log')

# app.run()

if __name__ == '__main__':
    # socketio = app.extensions['socketio']
    socketio.run(app,host='0.0.0.0',port=80)
