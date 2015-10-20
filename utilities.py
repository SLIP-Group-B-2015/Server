# Arthur Verkaik
# s1247563
# Utility functions for the server

import json
import uuid
from passlib.hash import pbkdf2_sha256
from server import db, Users, Raspberries, Events

def commitChange(newRow):
    db.session.add(newRow)
    db.session.commit()

def addUser(username, email, firstName, lastName, password):
    newUser = Users(userid=str(uuid.uuid4()), username=username, email=email, firstname=firstName, lastname=lastName, password=pbkdf2_sha256.encrypt(password, rounds=2000, salt_size=16))
    commitChange(newUser)

def addRaspberry(raspberryID, userID):
    newRaspberry = Raspberries(raspberryid=raspberryID, userid=userID)
    commitChange(newRaspberry)

def addEvent(raspberryID, eventID, description):
    newEvent = Events(raspberryid=raspberryID, eventid=eventID, description=description)
    commitChange(newEvent)