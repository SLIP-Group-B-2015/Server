'''
Arthur Verkaik
s1247563
Utility functions for the server
# TODO
  - Documentation for each function
  - db.rollbacks() where necessary
  - create testing functions (generateUsers, for example).
  - abstract away large queries.
  - add "INVALID EVENT TYPE" errors everywhere.
'''


import json
import uuid
from passlib.hash import pbkdf2_sha256
from server import db, Users, Raspberries, Events

def _commitChange(newRow):
    db.session.add(newRow)
    db.session.commit()

def checkUser(username, email):
    if (len(db.session.query(Users).filter(Users.email=email).all()) == 0 && \
        len(db.session.query(Users).filter(Users.username==username).all()) == 0):
        return True
    else:
        return False

# Return Boolean
def addUser(username, email, firstName, lastName, password):
    if (checkUser(username, email)):
        newUser = Users(userid=str(uuid.uuid4()), username=username, email=email, \
                        firstname=firstName, lastname=lastName, \
                        password=pbkdf2_sha256.encrypt(password, rounds=2000, salt_size=16))
        _commitChange(newUser)
        newUserID = Users.query.filter_by(username=username).with_entities(Users.userid).first()
        return newUserID.userid
    else:
        return False

# Return Boolean
def addRaspberry(raspberryID):
    existingRaspberries = Raspberries.query.filter_by(raspberryid=raspberryID).all()
    if (len(existingRaspberries) == 0):
        newRaspberry = Raspberries(raspberryid=raspberryID, userid=None)
        _commitChange(newRaspberry)
        return True
    else:
        return False

# Return boolean
def connectUserToRaspberry(userID, raspberryID):
    raspberryRow = Raspberries.query.filter_by(raspberryid=raspberryID).first()
    if raspberryRow.userid == None:
        raspberryRow.userid = userID
        db.session.commit()
        return True
    else:
        return False

# Return Boolean
def addEvent(raspberryID, eventType, eventTime, note, name):
    if (len(db.session.query(Events).filter(Events.raspberryid==raspberryID).\
            filter(Events.eventtype==eventType).filter(Events.eventtime==eventTime).\
            all()) > 0):
        return False
    newEvent = Events(raspberryid=raspberryID, eventtype=eventType, eventtime=eventTime, note=note, name=name)
    _commitChange(newEvent)
    return True

# Deals with pi POST requests. Returns a boolean (True = successfully added)
def piPosts(data, eventType):
    # possible event types: OPEN, CLOSE, KNOCK, MAIL, ID_SCAN
    eventTime = str(data[u'time'])
    raspberryID = str(data[u'raspberry'])
    note = None
    if data.get('note'):
        note = str(data[u'note'])
    fullName = None

    if eventType == 'ID_SCAN':
        userID = str(json.loads(inputJSON)[u'user'])
        bothNames = Users.query.filter_by(userid=userID).with_entities(Users.firstname,Users.lastname).all()
        fullName = bothNames[0][0] + ' ' + bothNames[0][1]

    return addEvent(raspberryID, eventType, eventTime, note, fullName)

# Deals with phone POST requests. Returns the UUID if successful. Returns False if not.
def phonePosts(data, eventType):
    # json format: {event:REGISTER, username:abc, email:abc@mail.com, firstName:ab, lastName:c, password:abcd}
    # event types: REGISTER

    if eventType == 'REGISTER':
        username = str(data[u'username'])
        password = str(data[u'password'])
        email = str(data[u'email'])
        firstName = str(data[u'firstName'])
        lastName = str(data[u'lastName'])
        return addUser(username, email, firstName, lastName, password)

    elif eventType == 'ADDPI':
        raspberryID = str(data[u'raspberryid'])
        userID = str(data[u'userid'])
        return connectUserToRaspberry(raspberryID, userID)

def postJSON(inputJSON):
    # phone event types - REGISTER, ADDPI
    # pi event types - ID_SCAN, KNOCK, MAIL, OPEN, CLOSE
    piEvents = ['ID_SCAN', 'KNOCK', 'MAIL', 'OPEN', 'CLOSE']
    phonePostEvents = ['REGISTER']
    data = json.loads(inputJSON)
    eventType = str(data[u'event'])

    if eventType in piEvents:
        return piPosts(data, eventType)
    elif eventType in phonePostEvents:
        return phonePosts(data, eventType)

 ##  {"event":"ID_SCAN","time":"Sat Oct 24 19:13:00 BST 2015","raspberry":"b673ab6f-182e-4c95-9715-ba8587fa33ca","user":"b673ab6f-182e-4c95-9715-ba8587fa33ca"}

def getEvents(eventType, userID, option):

    eventsBaseQuery = db.session.query(Events).filter(Users.userid==userID).\
                 filter(Users.userid==Raspberries.userid).\
                 filter(Raspberries.raspberryid==Events.raspberryid)
    if eventType == 'UNSENT':
        if option == 1:
            events = eventsBaseQuery.filter(Events.sent==False).all()
        elif option == 0:
            events = eventsBaseQuery.filter(Events.sent==False).\
                     filter(Events.eventtype!='OPEN').\
                     filter(Events.eventtype!='CLOSE').all()
    elif eventType == 'ALL':
        if option == 1:
            events = eventsBaseQuery.all()
        elif option == 0:
            events = eventsBaseQuery.filter(Events.eventtype!='OPEN').\
                     filter(Events.eventtype!='CLOSE').all()
    elif eventType in ['GETKNOCK', 'GETMAIL','GETID_SCAN']:
        events = eventsBaseQuery.filter(Events.eventtype==eventType[3:])

    return events

def phoneGets(events):
    jsonEventList = []

    for i in events:
        jsonEvent = {"raspberryID":i.raspberryid, "eventType":i.eventtype, "eventTime":str(i.eventtime), "note": i.note, "name": i.name}
        jsonEventList.append(jsonEvent)
        i.sent = True
        db.session.commit()

    return jsonEventList

def getPies(userID):
    raspberryIDList = []
    connectedRaspberries = Raspberries.query.filter(Raspberries.userid==userID).all()
    for i in connectedRaspberries:
        raspberry = {"raspberryID":i.raspberryid}
    return connectedRaspberries

def checkLogin(userID, password):
    hashedPassword =  Users.query.filter_by(userid=userID).with_entities(Users.password).all()
    return pbkdf2_sha256.verify(password, hashedPassword)

def getJSON(inputJSON):
    # Phone events (other than the list below): LOGIN, GETPI
    phoneGetEvents = ['ALL', 'UNSENT', 'GETKNOCK', 'GETMAIL', 'GETID_SCAN']
    data = json.loads(inputJSON)
    eventType = str(data[u'event'])

    if eventType in phoneGetEvents:
        userID = str(data[u'userid'])
        option = str(data[u'option'])
        events = getEvents(eventType, userID, option)
        jsonEventList = phoneGets(events)
        return json.dumps({'eventList': jsonEventList})

    elif eventType == 'LOGIN':
        # Deals with getting userID
        username = str(data[u'username'])
        userID = Users.query.filter(Users.username==username).with_entities(Users.userid).all()
        if len(userID) == 0:
            return json.dumps({'userid': 'DNE'})
        else:
            userID = userID[0].userid
        password = str(data[u'password'])
        if checkLogin(userID, password):
            return json.dumps({'userid': userID})
        else:
            return json.dumps({'userid': 'DNE'})

    elif eventType == 'GETPI':
        userID = str(data[u'userid'])
        raspberryList = getPies(userID)
        return json.dumps({'raspberryList': raspberryList})
