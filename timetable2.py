from functools import wraps

import flask
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import json
import pandas as pd
import sys, getopt, pprint
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo

from flask_pymongo import PyMongo

csvfile=open('C:\Users\한지훈\Desktop\시간표\시간표.csv','r')
jsonfile=open('C:\Users\한지훈\Desktop\test.json','a')
reader=csv.DictReader(csvfile)
header=["수강대상대학","수강대상학과","학수번호","분반","교과목명","영문교과목명",
        "학점","교과구분","공학인증구분","정원","현원","예비수강신청인원",
        "외국어강의","담당교수","주야","학년","요일시간","개설학과","강의계획서",
        "개설학과전화번호"]
for each in reader:
    row={}
    for field in header:
        row[field]=each[field]
    output.append(row)

json.dump(output, jsonfile, indent=None, sort_keys=False , encoding="UTF-8")
mongo_client=MongoClient() 
db=mongo_client.october_mug_talk
db.segment.drop()
data=pd.read_csv('C:\Program Files\MongoDB\test.json', error_bad_lines=0)
df = pd.DataFrame(data)
records = csv.DictReader(df)
db.segment.insert(records)

db.segment.find()


class LoginForm(FlaskForm):
    user_id = StringField('아이디', validators=[DataRequired()])
    user_pw = PasswordField('비밀번호', validators=[DataRequired()])

def login_required(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        if 'user' not in flask.session:
            flask.flash('로그인을 해주세요.', 'error')
            return flask.redirect(flask.url_for('login'))

        return view(*args, **kwargs)
    return decorated_view

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'eilfjdksasfae'
app.config['MONGO_DBNAME'] = 'test'

mongo = PyMongo(app)

@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in flask.session:
        flask.flash('이미 로그인 되어 있습니다.', 'info')
        return flask.redirect(flask.url_for('index'))

    login_form = LoginForm()
    if flask.request.method == 'POST' and login_form.validate():
        user_id = login_form.user_id.data
        user_pw = login_form.user_pw.data

        user = mongo.db.users.find_one({'id': user_id})
        if not user:
            flask.flash('존재하지 않는 아이디입니다.', 'error')
            return flask.redirect(flask.url_for('login'))

        if check_password_hash(user['pw_hash'], user_pw):
            flask.session['user'] = {
                'id': user['id'],
                'name': user['name'],
            }
            return flask.redirect(flask.url_for('index'))
        else:
            flask.flash('비밀번호가 틀렸습니다.', 'error')
            return flask.redirect(flask.url_for('login'))

        return flask.redirect(flask.url_for('index'))

    return flask.render_template('login.html', login_form=login_form)

@app.route('/logout')
def logout():
    flask.session.pop('user', None)
    return flask.redirect(flask.url_for('index'))


@app.route('/timeTable')
def timeTable(): #시간표를 보여줌 - 시간표 DB에서 저장된 내용 요일, 시작시간, 종료시간, 과목명
    Tables1 = mongo.db.timetable.find({'day':"Monday"})
    Tables2 = mongo.db.timetable.find({'day':"Tuesday"})
    Tables3 = mongo.db.timetable.find({'day':"Wednesday"})
    Tables4 = mongo.db.timetable.find({'day':"Thursday"})
    Tables5 = mongo.db.timetable.find({'day':"Friday"})

    count1=0
    count2=0
    dataevents = [
    "event-1",
    "event-2",
    "event-3",
    "event-4",
    ]
    contents = [
    "event-restorative-yoga",
    "event-rowing-workout",
    "event-abs-circuit",
    "event-yoga-1",
    ]
    return flask.render_template("timeTable.html",
     Tables1=Tables1,Tables2=Tables2,Tables3=Tables3,Tables4=Tables4,Tables5=Tables5
     , contents=contents, count1=count1, count2=count2, dataevents=dataevents)


@app.route('/searchTable')
def searchTable():
    Searches = mongo.db.searchtable.find()
    return flask.render_template("searchTable.html",Searches=Searches)

@app.route('/newTable/<ObjectId:id>')
def newTable(id):
    searchId = mongo.db.searchtable.find_one({'_id': id})
    if 'q' in searchId.keys():
        day = searchId.get('q')[:1]
        if day == "월":
            day = "Monday"
        elif day == "화":
            day = "Tuesday"
        elif day == "수":
            day = "Wednesday"
        elif day == "목":
            day = "Thursday"
        elif day == "금":
            day = "Friday"

        split = searchId.get('q').find('-')
        startTime = searchId.get('q')[split-5:split]
        endTime = searchId.get('q')[split+1:split+6]
        name = searchId.get('e')
        mongo.db.timetable.insert_one({'day':day,'starttime':startTime,'endtime':endTime, 'name':name})
        return flask.redirect(flask.url_for('searchTable'))
    return flask.redirect(flask.url_for('searchTable'))