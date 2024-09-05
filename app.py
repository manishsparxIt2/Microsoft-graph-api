from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from utils.basic_utils import db
import os
import sys
import base64

from sqlalchemy import create_engine ,text
basedi = os.path.abspath(os.path.dirname(__file__))
import pandas as pd

if getattr(sys ,'freez' ,False):
    bundle_dir =  sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__)
   # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    #db = SQLAlchemy(app)
    app.secret_key = "ThisIsNotASecret:p"
    app.config.from_pyfile(os.path.join(bundle_dir,'config.py'))
    #db.create_all()
    db.init_app(app)
    return app

app =create_app()
with app.app_context():
    db.Model.metadata.reflect(db.engine)
    db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('index.html', message="Hello!")



@app.template_filter('b64decode')
def b64decode_filter(encoded_str):
    """Decodes a Base64 encoded string."""
    return base64.b64decode(encoded_str).decode('utf-8')


@app.route('/show/<email_type>', methods=['GET'])
def showEmails(email_type):
    print(email_type)
    sql = "select *  FROM o365.tbl_emails where lower(email_type)  = '"+email_type.lower()+"' order by  date_added DESC"
    #print(sql)
    df = pd.read_sql_query(sql,db.engine)

    data = df.to_dict(orient='records')
    # print(data)
    # for row in data:
    #     print(row['id'])
    # for index, data in df.iterrows():
    #     print(data['email_type'])
    return render_template('tables.html' ,data=data)

@app.route('/dashboard/', methods=['GET'])
def dashboard():
    #db.
    sql = "select count(1) as cnt , email_type  from o365.tbl_emails te  group by  2"
    result_data = dict()
    with db.engine.connect() as connection:
        result = connection.execute(text(sql))
        result = result
        for data in result:
            result_data[data[1]] = data[0]            
    
    sql_user_count = "SELECT count(1) as cnt FROM o365.tbl_email_users;"
    with db.engine.connect() as connection:
        result = connection.execute(text(sql_user_count))
        
        for data in result:
            totaluser = data[0]
    return render_template('index.html' ,result_data=result_data ,totaluser=totaluser)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('index.html', message="Incorrect Details")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

if(__name__ == '__main__'):   
    app.run(debug=True)
