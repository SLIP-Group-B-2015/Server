# Arthur Verkaik
# s1247563
# Utility functions for the server

# TODO
# - Document each functions
# - Create new function for retrieving events/users using the raspberryID.

import json
import uuid
from passlib.hash import pbkdf2_sha256
from server import db, Users, Raspberries, Events

def _commitChange(newRow):
    db.session.add(newRow)
    db.session.commit()

# Return UUID
def addUser(username, email, firstName, lastName, password):
    newUser = Users(userid=str(uuid.uuid4()), username=username, email=email, firstname=firstName, lastname=lastName, password=pbkdf2_sha256.encrypt(password, rounds=2000, salt_size=16))
    _commitChange(newUser)
    newUserID = str(Users.query.filter_by(username=username).with_entities(Users.userid).all())
    return newUserID[3:-4]

# Return Boolean
def addRaspberry(raspberryID):
    existingRaspberries = Raspberries.query.filter_by(raspberryid=raspberryID).all()
    if (len(existingRaspberries) == 0):
        newRaspberry = Raspberries(raspberryid=raspberryID, userid=None)
        _commitChange(newRaspberry)
        return True
    else:
        return False

# Return void
def addEvent(raspberryID, eventType, eventTime, note, name):
    newEvent = Events(raspberryid=raspberryID, eventtype=eventType, eventtime=eventTime, note=note, name=name)
    _commitChange(newEvent)


def unpackJSON(inputJSON):
    # event types - ID_SCAN, KNOCK, MAIL, OPEN, CLOSE
    data = json.loads(inputJSON)
    eventType = str(json.loads(inputJSON)[u'event'])
    eventTime = str(json.loads(inputJSON)[u'time'])
    raspberryID = str(json.loads(inputJSON)[u'raspberry'])
    note = None
    if data.get('note'):
        note = str(json.loads(inputJSON)[u'note'])
    name = None

    if eventType == 'ID_SCAN':
        userID = str(json.loads(inputJSON)[u'user'])
        bothNames = Users.query.filter_by(userid=userID).with_entities(Users.firstname,Users.lastname).all()
        firstName = bothNames[0][0]
        lastName = bothNames[0][1]
        name = firstName + ' ' + lastName

    addEvent(raspberryID, eventType, eventTime, note, name)
