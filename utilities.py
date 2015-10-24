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
def addEvent(raspberryID, eventID, eventTime, description):
    newEvent = Events(raspberryid=raspberryID, eventid=eventID, eventtime=eventTime, description=description)
    _commitChange(newEvent)


def unpackJSON(json):
    # event types - ID_SCAN, KNOCK, MAIL, OPEN, CLOSE
    eventType = str(json.loads(json)[u'event'])
    eventTime = str(json.loads(json))[u'time']
    raspberryID = str(json.loads(json))[u'raspberry']

    if eventType == 'ID_SCAN':
        userID = str(json.loads(json))[u'user']
        username = str(Users.query.filter_by(userid=userID).with_entities(Users.username).all())[4:-4]
        description = "%s was at your door!" % (username)
    elif eventType == 'KNOCK':
        description = "Someone knocked at your door!"
    elif eventType == 'MAIL':
        description = "You received mail!"
    elif eventType == 'OPEN':
        description = "Your door was opened!"
    elif eventType == 'CLOSE':
        description = "Your door was closed!"

    addEvent(raspberryID, eventType, eventTime, description)
