from functools import wraps

import flask
import re
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo

from flask_pymongo import PyMongo

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

@app.route('/searchTable/<int:num>', methods=['GET', 'POST'])
def searchTable(num):
    if flask.request.method == "POST":
        if flask.request.form['major']:
            Searches = mongo.db.courselist.find({'b':flask.request.form['major']})
        if flask.request.form['classname']:
            Searches = mongo.db.courselist.find({'e':flask.request.form['classname']})
        if flask.request.form['classnumber']:
            Searches = mongo.db.courselist.find({'c':flask.request.form['classnumber']})
        else:
            return flask.redirect(flask.url_for("searchTable", num='0'))
        return flask.render_template("searchTable.html",Searches=Searches)
    else:
        if num == 0:
            Searches = mongo.db.courselist.find().limit(60)
        elif num == 1:
            Searches = mongo.db.courselist.find().skip(60).limit(120)
        elif num == 2:
            Searches = mongo.db.courselist.find().skip(120).limit(180)
        elif num == 3:
            Searches = mongo.db.courselist.find().skip(180).limit(240)
        elif num == 4:
            Searches = mongo.db.courselist.find().skip(240)
        else:
            Searches = mongo.db.courselist.find()
    return flask.render_template("searchTable.html",Searches=Searches)

@app.route('/newTable/<ObjectId:id>')
def newTable(id):
    searchId = mongo.db.courselist.find_one({'_id': id})
    string = searchId.get('q')
    name = searchId.get('e')

    if len(string)<30:
        p=re.compile(r"(\w)")
        m=p.search(string)
        day1 = m.group(0)#searchId.get('q')[:1]
        if day1 == "월" or day1 == " 월":
            day1 = "Monday"
        elif day1 == "화" or day1 == " 화":
            day1 = "Tuesday"
        elif day1 == "수" or day1 == " 수":
            day1 = "Wednesday"
        elif day1 == "목" or day1 == " 목":
            day1 = "Thursday"
        elif day1 == "금" or day1 == " 금":
            day1 = "Friday"
        elif day1 == "토" or day1 == " 토":
            day1 = "Saturday"
        elif day1 == "일" or day1 == " 일":
            day1 == "Sunday"

        p = re.compile("(?=[(]).+")
        m=p.search(string)
        p=re.compile(r"[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)")
        m=p.search(string)
        start1 = m.group(1)+':'+m.group(2)
        end1 = m.group(3)+':'+m.group(4)
        #r1 = m.group(1)+':'+m.group(2)+'~'+m.group(3)+':'+m.group(4)
 # 시간표 DB에서 같은요일의 다른 과목들과 비교
        searchAll = mongo.db.timetable.find({'day':day1})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end1 <= compare_start or compare_end <= start1 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
                        # return flask.flash("이미 등록된 강의입니다.")
        mongo.db.timetable.insert_one({'day':day1,'starttime':start1,'endtime':end1, 'name':name})
        return flask.redirect(flask.url_for("searchTable", num='0'))
        # return flask.flash("시간표에 등록 되었습니다.")

    elif len(string)>30 and len(string)<60:
        p=re.compile(r"(\w)")
        m=p.search(string)
        day1 = m.group(0)#searchId.get('q')[:1]
        if day1 == "월" or day1 == " 월":
            day1 = "Monday"
        elif day1 == "화" or day1 == " 화":
            day1 = "Tuesday"
        elif day1 == "수" or day1 == " 수":
            day1 = "Wednesday"
        elif day1 == "목" or day1 == " 목":
            day1 = "Thursday"
        elif day1 == "금" or day1 == " 금":
            day1 = "Friday"
        elif day1 == "토" or day1 == " 토":
            day1 = "Saturday"
        elif day1 == "일" or day1 == " 일":
            day1 == "Sunday"
        p = re.compile("(?=[(]).+")
        m=p.search(string)
        p=re.compile(r"[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)")
        m=p.search(string)
        start1 = m.group(1)+':'+m.group(2)
        end1 = m.group(3)+':'+m.group(4)

        p=re.compile(r"\s+(\w)")
        m=p.search(string)
        day2 = m.group(0)#searchId.get('q')[searchId.find(' ')-1:searchId.find(' ')]
        if day2 == "월" or day2 == " 월":
            day2 = "Monday"
        elif day2 == "화" or day2 == " 화":
            day2 = "Tuesday"
        elif day2 == "수" or day2 == " 수":
            day2 = "Wednesday"
        elif day2 == "목" or day2 == " 목":
            day2 = "Thursday"
        elif day2 == "금" or day2 == " 금":
            day2 = "Friday"
        elif day2 == "토" or day2 == " 토":
            day1 = "Saturday"
        elif day2 == "일" or day2 == " 일":
            day1 == "Sunday"
        p=re.compile(r"(\w)+((?=[(]).+)+[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)")
        m=p.search(string)
        #print(m.group(3)+':'+m.group(4)+'~'+m.group(5)+':'+m.group(6))

        start2 = m.group(3)+':'+m.group(4)
        end2 = m.group(5)+':'+m.group(6)

        searchAll = mongo.db.timetable.find({'day':day1})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end1 <= compare_start or compare_end <= start1 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day1,'starttime':start1,'endtime':end1, 'name':name})
        searchAll = mongo.db.timetable.find({'day':day2})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end2 <= compare_start or compare_end <= start2 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
                    return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day2,'starttime':start2,'endtime':end2, 'name':name})
        return flask.redirect(flask.url_for("searchTable", num='0'))

    elif len(string)>60 and len(string)<90:
        p = re.compile(
        r"(\w)(\d)\s+[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)+[)(]+[\w+]+[-]+[\d+]+[)]\s+(\w)(\d)\s+[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)+[)(]+[\w+]+[-]+[\d+]+[)]\s+(\w)(\d)\s+[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)+[)(]+[\w+]+[-]+[\d+]+[)]")
        m = p.search(string)
        day1 = m.group(1)#searchId.get('q')[:1]
        day2 = m.group(7)#searchId.get('q')[searchId.find(' ')-1:searchId.find(' ')]
        day3 = m.group(13)#searchId.get('q')[searchId.rfind(' ')-1:searchId.rfind(' ')]


        start1 = m.group(3)+':'+m.group(4)
        end1 = m.group(5)+':'+m.group(6)
        start2 = m.group(9)+':'+m.group(10)
        end2 = m.group(11)+':'+m.group(12)
        start3 = m.group(15)+':'+m.group(16)
        end3 = m.group(17)+':'+m.group(18)
        r1 = m.group(3)+':'+m.group(4)+'~'+m.group(5)+':'+m.group(6)
        r2 = m.group(9)+':'+m.group(10)+'~'+m.group(11)+':'+m.group(12)
        r3 = m.group(15)+':'+m.group(16)+'~'+m.group(17)+':'+m.group(18)
        searchAll = mongo.db.timetable.find({'day':day1})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end1 <= compare_start or compare_end <= start1 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day1,'starttime':start1,'endtime':end1, 'name':name})
        searchAll = mongo.db.timetable.find({'day':day2})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end2 <= compare_start or compare_end <= start2 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day2,'starttime':start2,'endtime':end2, 'name':name})
        searchAll = mongo.db.timetable.find({'day':day3})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end3 <= compare_start or compare_end <= start3 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day3,'starttime':start3,'endtime':end3, 'name':name})
        return flask.redirect(flask.url_for("searchTable", num='0'))

    else:
        p = re.compile(
        r"(\w)(\d)\s+[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)+[)(]+[\w+]+[-]+[\d+]+[)]\s+(\w)(\d)\s+[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)+[)(]+[\w+]+[-]+[\d+]+[)]\s+(\w)(\d)\s+[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)+[)(]+[\w+]+[-]+[\d+]+[)]\s+(\w)(\d)\s+[(]+(\d+)+[:]+(\d+)+[-]+(\d+)+[:]+(\d+)+[)(]+[\w+]+[-]+[\d+]+[)]")
        m = p.search(string)
        day1 = m.group(1)#searchId.get('q')[:1]
        day2 = m.group(7)#searchId.get('q')[searchId.find(' ')-1:searchId.find(' ')]
        day3 = m.group(13)#searchId.get('q')[47:][searchId.find(' ')-1:searchId.find(' ')]
        day4 = m.group(19)#searchId.get('q')[searchId.rfind(' ')-1:searchId.rfind(' ')]
        
        start1 = m.group(3)+':'+m.group(4)
        end1 = m.group(5)+':'+m.group(6)
        start2 = m.group(9)+':'+m.group(10)
        end2 = m.group(11)+':'+m.group(12)
        start3 = m.group(15)+':'+m.group(16)
        end3 = m.group(17)+':'+m.group(18)
        start4 = m.group(21)+':'+m.group(22)
        end4 = m.group(23)+':'+m.group(24)
        m.group(3)+':'+m.group(4)+'~'+m.group(5)+':'+m.group(6)
        m.group(9)+':'+m.group(10)+'~'+m.group(11)+':'+m.group(12)
        m.group(15)+':'+m.group(16)+'~'+m.group(17)+':'+m.group(18)
        m.group(21)+':'+m.group(22)+'~'+m.group(23)+':'+m.group(24)
        searchAll = mongo.db.timetable.find({'day':day1})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end1 <= compare_start or compare_end <= start1 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day1,'starttime':start1,'endtime':end1, 'name':name})
        searchAll = mongo.db.timetable.find({'day':day2})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end2 <= compare_start or compare_end <= start2 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day2,'starttime':start2,'endtime':end2, 'name':name})
        searchAll = mongo.db.timetable.find({'day':day3})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end3 <= compare_start or compare_end <= start3 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day3,'starttime':start3,'endtime':end3, 'name':name})
        searchAll = mongo.db.timetable.find({'day':day4})
        for sAll in searchAll:
            if sAll['_id'] != searchId['_id']:
                    compare_start = sAll.get('starttime')
                    compare_end = sAll.get('endtime')
                    if not( end3 <= compare_start or compare_end <= start4 ):
                        return flask.redirect(flask.url_for("searchTable", num='0'))
        mongo.db.timetable.insert_one({'day':day4,'starttime':start4,'endtime':end4, 'name':name})
        return flask.redirect(flask.url_for("searchTable", num='0'))

    # if 'q' in searchId.keys():
    #     day = searchId.get('q')[:1]

    #     split = searchId.get('q').find('-')
    #     startTime = searchId.get('q')[split-5:split]
    #     endTime = searchId.get('q')[split+1:split+6]
    #     name = searchId.get('e')

    #     start_f = searchId.get('q')[split-5:split-3]
    #     start_r = searchId.get('q')[split-2:split]
    #     end_f = searchId.get('q')[split+1:split+3]
    #     end_r = searchId.get('q')[split+4:split+6]

    #     searchAll = mongo.db.courselist.find({'day':day}) # 같은요일의 다른 과목들과 비교
    #     for sAll in searchAll:
    #         compare_split = sAll.get('q').find('-')
    #         compare_start_f = sAll.get('q')[compare_split-5:compare_split-3]
    #         compare_start_r = sAll.get('q')[compare_split-2:compare_split]
    #         compare_end_f = sAll.get('q')[compare_split+1:compare_split+3]
    #         compare_end_r = sAll.get('q')[compare_split+4:compare_split+6]

    #         if not( int(end_f)*100+int(end_r)<=int(compare_start_f)*100+int(compare_start_r) or 
    #                 int(compare_end_f)*100+int(compare_end_r)<=int(start_f)*100+int(start_r) ):
    #            return flask.redirect(flask.url_for('timeTable'))
                # 하나라도 if문을 통과하지 못하면 db에 값을 못넣는다.
        # mongo.db.timetable.insert_one({'day':day,'starttime':startTime,'endtime':endTime, 'name':name})
    #return flask.redirect(flask.url_for('searchTable'))