from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from utilities import *

# Configurations
USERNAME = "admin" # (temporary check until database is working)
PASSWORD = "password"

# Create app object
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///slipDB'
app.config['SQLALCHEMY_NATIVE_UNICODE'] = True
db = SQLAlchemy(app)

@app.route('/', methods=['POST', 'GET'])
def home(name=None):
    if request.method == 'POST':
        jsonMsg = request.json
        #print(jsonMsg)
        print(json.dumps(jsonMsg))
        if (json is not None):
            print("\nUnpacking JSON")
            unpackJSON(json.dumps(json))
            print("JSON unpacked!")
        return "This is a test! It works!"
    else:
        return test()

@app.route('/test/')
def test():
    json = request.json
    print(json)
    if json is not None:
        unpackJSON(json.dumps(json))
        print("\nJSON unpacked")
    return 'The web site you are trying to reach is undergoing construction by a team of highly trained monkies. Thank you for visiting'

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
    raspberryid = db.Column(UUID, primary_key=True)
    userid = db.Column(UUID, db.ForeignKey('users.userid'))

    def __repr__(self):
        return '<Raspberry %r>' % self.raspberryid

# Events Table
class Events(db.Model):
    raspberryid = db.Column(UUID, db.ForeignKey('raspberries.raspberryid'), primary_key=True)
    eventtype = db.Column(db.String(10), nullable=False, primary_key=True)
    eventtime = db.Column(db.DateTime, default=datetime.now(), primary_key=True)
    note = db.Column(db.Text)
    name = db.Column(db.String(50))
    sent = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Raspberry %r, EventType %r, EventTime %r, Sent %r>' % (self.raspberryid, self.eventtype, self.eventtime, self.sent)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)

# Example query, which gets the events which are linked to the user 'marshall'

# query = db.session.query(Events).\
# filter(Users.userid == Raspberries.userid).\
# filter(Users.username == "marshall").\
# filter(Raspberries.raspberryid == Events.raspberryid).all()
