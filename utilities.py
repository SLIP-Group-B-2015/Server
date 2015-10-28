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

    if (db.session.query(Events).filter(Events.raspberryid==raspberryID).filter(Events.eventtype==eventType).filter(Events.eventtime==eventTime).all() > 0):
        addEvent(raspberryID, eventType, eventTime, note, name)

    return "Event successfully added!"
 ##  {"event":"ID_SCAN","time":"Sat Oct 24 19:13:00 BST 2015","raspberry":"b673ab6f-182e-4c95-9715-ba8587fa33ca","user":"b673ab6f-182e-4c95-9715-ba8587fa33ca"}
def generateJSON(inputJSON):
    userID = str(json.loads(inputJSON)[u'userid'])
    unsentEvents = db.session.query(Events).filter(Users.userid==userID).filter(Users.userid==Raspberries.userid).filter(Raspberries.raspberryid==Events.raspberryid).filter(Events.sent==False).all()
    eventList = []
    for i in unsentEvents:
        event = {"eventType": i.eventtype, "eventtime": str(i.eventtime), "note": i.note, "name": i.name}
        eventList.append(event)
        i.sent = True
        db.session.commit()

    return json.dumps({'newEvents': eventList})
