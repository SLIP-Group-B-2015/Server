from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
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
        return "This is a test! It works! %s username" % request.form['username']
    else:
        return "It failed"

@app.route('/test/')
def test():
    return 'The web site you are trying to reach is undergoing construction by a team of highly trained monkies. Please visit another time!'

# Database Schema
# Users Table
class Users(db.Model):
    userid = db.Column(UUID, primary_key=True)
    username = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Raspberries Table
class Raspberries(db.Model):
    raspberryid = db.Column(UUID, primary_key=True)
    userid = db.Column(UUID, db.ForeignKey('user.userid'))
    
# Events Table
class Events(db.Model):
    raspberryid = db.Column(UUID, db.ForeignKey('raspberries.raspberryid'), primary_key=True)
    eventid = db.Column(db.String(10), nullable=False, primary_key=True)
    eventtime = db.Column(db.DateTime, default=datetime.utcnow(), primary_key=True)
    description = db.Column(db.Text)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
