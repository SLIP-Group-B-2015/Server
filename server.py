from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
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
            #print("JSON unpacked!\n")
            #return "This is a test! It works!"
        return "No JSON was detected."
    else:
        # App requests updates from server
        print("\n" + json.dumps(jsonMsg))
        if jsonMsg is not None:
            return getJSON(json.dumps(jsonMsg)) # Get requests should return JSON object with relevant info
        return "No JSON was detected."

# @app.route('/getRequest/')
# def getRequest(jsonMsg):
#     if jsonMsg is not None:
#         print("\n" + json.dumps(jsonMsg))
#         return getJSON(json.dumps(jsonMsg)) # Get requests should return JSON object with relevant info
#     return "No JSON was detected."


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
    raspberryname = db.Column(db.String(30))

    def __repr__(self):
        return '<Raspberry %r, id %r>' % (self.raspberryname, self.raspberryid)

# Events Table
class Events(db.Model):
    raspberryid = db.Column(UUID, primary_key=True)
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
