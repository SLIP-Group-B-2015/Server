from flask import Flask, request, render_template, redirect, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from passlib.hash import pbkdf2_sha256
import pytz
from flask.ext.login import LoginManager, login_user , logout_user , current_user , login_required
from datetime import datetime

from utilities import *

# Create app object
app = Flask(__name__)
# DEBUG MUST BE TURNED OFF WHEN SERVER READY FOR DISTRIBUTION
app.debug = True
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///slipDB'
app.config['SQLALCHEMY_NATIVE_UNICODE'] = True
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'super secret key'

tz = pytz.timezone('Europe/London')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    return Users.query.filter_by(userid=userid).first()

@app.route('/', methods=['POST', 'GET'])
def home(name=None):
    print request
    jsonMsg = request.json
    if request.method == 'POST':
        # Server is receiving JSON
        print("\n" + json.dumps(jsonMsg))
        if (jsonMsg is not None):
            print("Unpacking JSON")
            return postJSON(json.dumps(jsonMsg))
        return redirect(url_for('login'))
    else:
        # App requests updates from server
        print("\n" + json.dumps(jsonMsg))
        if jsonMsg is not None:
            return getJSON(json.dumps(jsonMsg)) # Get requests should return JSON object with relevant info
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    print request
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        registered_user = verifyCredentials(username, password)
        if registered_user is None:
            error = True
        else:
            login_user(registered_user)
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)

@app.route('/registerUser', methods=['GET', 'POST'])
def register():
    error = None
    print request
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        registered_user = checkUser(username, email)
        if registered_user:
            error = True
        else:
            # Available credentials, insert into DB and login
            addUser(username, email, firstname, lastname, password)
            user = verifyCredentials(username, password)
            login_user(user)
            return redirect(url_for('timeline'))
    return render_template('registerUser.html', error=error)

@app.route('/timeline')
@login_required
def timeline():
    events = getUserEvents(current_user.userid)

    return render_template('timeline.html', events=events)  # render the user's timeline

def verifyCredentials(username, password):
    hashedPassword = Users.query.filter_by(username=username).with_entities(Users.password).first()
    if hashedPassword is None:
        return None
    if pbkdf2_sha256.verify(password, hashedPassword.password):
        return Users.query.filter_by(username=username).first()
    else:
        return None

def getUserEvents(userid):
    eventList = []

    events = db.session.query(Connections,Events).filter(userid==Connections.userid,Connections.raspberryid==Events.raspberryid).all()

    for event in events:

        if event[0].raspberryname is None:
            name = "Unknown"
        else:
            name = event[0].raspberryname

        dictEvent = {"raspberryName": name, "eventType":event[1].eventtype, "eventTime":event[1].eventtime,
                     "note": event[1].note, "name": event[1].name}
        eventList.append(dictEvent)

    retlist = sorted(eventList, key=lambda k: k['eventTime'], reverse=True)

    for element in retlist:
        element["eventTime"] = element["eventTime"].strftime("%H:%M on %A %d %B %Y")

    return retlist

# Database Schema
# Written by Arthur Verkaik

# Users Table
class Users(db.Model):
    userid = db.Column(UUID, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, userid, username, email, firstname, lastname, password):
        self.userid = userid
        self.username = username
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.userid)

    def __repr__(self):
        return '<User %s>' % self.username

# Raspberries Table
class Connections(db.Model):
    raspberryid = db.Column(UUID, db.ForeignKey('connections.raspberryid'), primary_key=True)
    userid = db.Column(UUID, db.ForeignKey('users.userid'), primary_key=True)
    raspberryname = db.Column(db.String(30))

    def __repr__(self):
        return '<Raspberry %r, UserId %r>' % (self.raspberryid, self.userid)

# Events Table
class Events(db.Model):
    raspberryid = db.Column(UUID, db.ForeignKey('connections.raspberryid'), primary_key=True)
    eventtype = db.Column(db.String(10), nullable=False, primary_key=True)
    eventtime = db.Column(db.DateTime, default=datetime.now(tz), primary_key=True)
    note = db.Column(db.Text)
    name = db.Column(db.String(50))
    sent = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Raspberry %r, EventType %r, EventTime %r, Sent %r>' % (self.raspberryid, self.eventtype, self.eventtime, self.sent)

# RaspberryNames table
class Raspberries(db.Model):
    raspberryid = db.Column(UUID, primary_key=True)

    def __init__(self, raspberryid):
        self.raspberryid = raspberryid

    def __repr__(self):
        return '<Raspberry %r>' % (self.raspberryid)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)
