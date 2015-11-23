from flask import Flask, request, render_template, redirect, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from passlib.hash import pbkdf2_sha256
import pytz
import uuid

from utilities import *

# Create app object
app = Flask(__name__)
# DEBUG MUST BE TURNED OFF WHEN SERVER READY FOR DISTRIBUTION
app.debug = True
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///slipDB'
app.config['SQLALCHEMY_NATIVE_UNICODE'] = True
db = SQLAlchemy(app)

tz = pytz.timezone('Europe/London')

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
        if verifyCredentials(username, password):
            return redirect(url_for('timeline'))
        else:
            error = True
    return render_template('login.html', error=error)

@app.route('/timeline')
@login_required(login_url=url_for('login'))
def timeline():
    return render_template('timeline.html')  # render the user's timeline

def verifyCredentials(username, password):
    hashedPassword = Users.query.filter_by(username=username).with_entities(Users.password).first()
    if hashedPassword == None:
        return False
    return pbkdf2_sha256.verify(password, hashedPassword.password)

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

    def __repr__(self):
        return '<User %s>' % self.username

# Raspberries Table
class Raspberries(db.Model):
    raspberryid = db.Column(UUID, db.ForeignKey('raspberry_names.raspberryid'), primary_key=True)
    userid = db.Column(UUID, db.ForeignKey('users.userid'), primary_key=True)
    def __repr__(self):
        return '<Raspberry %r, UserId %r>' % (self.raspberryid, self.userid)

# Events Table
class Events(db.Model):
    raspberryid = db.Column(UUID, db.ForeignKey('raspberry_names.raspberryid'), primary_key=True)
    eventtype = db.Column(db.String(10), nullable=False, primary_key=True)
    eventtime = db.Column(db.DateTime, default=datetime.now(tz), primary_key=True)
    note = db.Column(db.Text)
    name = db.Column(db.String(50))
    sent = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Raspberry %r, EventType %r, EventTime %r, Sent %r>' % (self.raspberryid, self.eventtype, self.eventtime, self.sent)

# RaspberryNames table
class Raspberry_names(db.Model):
    raspberryid = db.Column(UUID, primary_key=True)
    raspberryname = db.Column(db.String(30))

    def __repr__(self):
        return '<Raspberry %r, Name %r>' % (self.raspberryid, self.raspberryname)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)