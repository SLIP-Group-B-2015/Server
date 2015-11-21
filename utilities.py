'''
Arthur Verkaik
s1247563
Utility functions for the server
# TODO
  - Documentation for each function
  - db.rollbacks() where necessary
  - properly throw/catch errors
  - create testing functions (generateUsers, for example).
  - abstract away large queries.
  - add "INVALID EVENT TYPE" errors everywhere.
  - postJSON should only return False if the data is not in the database when
    returning False.
  - debug getEvents
'''


import json
import uuid
from passlib.hash import pbkdf2_sha256
from server import db, Users, Raspberries, Events, Raspberry_names

def _commitChange(newRow, noError):
    try:
        db.session.add(newRow)
        db.session.commit()
    except:
        db.session.rollback()
        noError = False
        raise

    return noError

def checkUser(username, email):
    if len(Users.query.filter_by(email=email).all()) == 0 and len(Users.query.filter_by(username=username).all()) == 0:
        return True
    else:
        return False

# Return Boolean
def addUser(username, email, firstName, lastName, password):
    if (checkUser(username, email)):
        newUser = Users(userid=str(uuid.uuid4()), username=username, email=email, \
                        firstname=firstName, lastname=lastName, \
                        password=pbkdf2_sha256.encrypt(password, rounds=2000, salt_size=16))
        _commitChange(newUser, True)
        newUserID = Users.query.filter_by(username=username).with_entities(Users.userid).first()
        return newUserID.userid
    else:
        return False

# Return Boolean
def addRaspberry(raspberryID):
    print(raspberryID)
    existingRaspberries = Raspberry_names.query.filter_by(raspberryid=raspberryID).all()
    if (len(existingRaspberries) == 0):
        newRaspberryName = Raspberry_names(raspberryid=raspberryID, raspberryname=None)
        _commitChange(newRaspberryName, True)
        return True
    else:
        return False

# Return boolean
def connectUserToRaspberry(userID, raspberryID, raspberryName):
    #print(raspberryID)
    raspberryNameRow = db.session.query(Raspberry_names).filter(Raspberry_names.raspberryid==raspberryID).first()
    #print(raspberryNameRow)

    if raspberryNameRow != None:
        newRaspberryConnection = Raspberries(raspberryid=raspberryID, userid=userID)
        db.session.add(newRaspberryConnection)

        if raspberryNameRow.raspberryname == None:
            raspberryNameRow.raspberryname = raspberryName

        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            raise
    else:
        return False

# Return Boolean
def addEvent(raspberryID, eventType, eventTime, note, name):
    if (len(db.session.query(Events).filter(Events.raspberryid==raspberryID).\
            filter(Events.eventtype==eventType).filter(Events.eventtime==eventTime).\
            all()) > 0):
        return True

    newEvent = Events(raspberryid=raspberryID, eventtype=eventType, eventtime=eventTime, note=note, name=name)
    return _commitChange(newEvent, True)

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
        userID = str(data[u'user'])
        bothNames = Users.query.filter_by(userid=userID).with_entities(Users.firstname,Users.lastname).all()
        fullName = bothNames[0][0] + ' ' + bothNames[0][1]

    return str(addEvent(raspberryID, eventType, eventTime, note, fullName))

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
        userID = str(addUser(username, email, firstName, lastName, password))
        return json.dumps({'userid': userID})

    elif eventType == 'ADDPI':
        raspberryID = str(data[u'raspberryid'])
        userID = str(data[u'userid'])
        raspberryName = str(data[u'raspberryname'])
        added = str(connectUserToRaspberry(userID, raspberryID, raspberryName))
        return json.dumps({'added': added})

def postJSON(inputJSON):
    # phone event types - REGISTER, ADDPI
    # pi event types - ID_SCAN, KNOCK, MAIL, OPEN, CLOSE
    piEvents = ['ID_SCAN', 'KNOCK', 'MAIL', 'OPEN', 'CLOSE']
    phonePostEvents = ['REGISTER', 'ADDPI']
    data = json.loads(inputJSON)
    eventType = str(data[u'event'])

    if eventType in piEvents:
        return piPosts(data, eventType)
    elif eventType in phonePostEvents:
        return phonePosts(data, eventType)

 ##  {"event":"ID_SCAN","time":"Sat Oct 24 19:13:00 BST 2015","raspberry":"b673ab6f-182e-4c95-9715-ba8587fa33ca","user":"b673ab6f-182e-4c95-9715-ba8587fa33ca"}

def getEvents(eventType, userID, option):
    events = []
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
        try:
            i.sent = True
            db.session.commit()
        except:
            db.session.rollback()

    return jsonEventList

def getPies(userID):
    raspberryList = []
    connectedRaspberries = Raspberries.query.filter(Raspberries.userid==userID).all()
    for i in connectedRaspberries:
        raspberryName = Raspberry_names.query.filter(Raspberry_names.raspberryid==i.raspberryid).first()
        raspberryName = raspberryName.raspberryname
        raspberry = {"raspberryID":i.raspberryid, "raspberryName":raspberryName}
        raspberryList.append(raspberry)
    return raspberryList

def checkLogin(userID, password):
    hashedPassword =  Users.query.filter_by(userid=userID).with_entities(Users.password).first()
    return pbkdf2_sha256.verify(password, hashedPassword.password)

def getJSON(inputJSON):
    # Phone events (other than the list below): LOGIN, GETPI
    phoneGetEvents = ['ALL', 'UNSENT', 'GETKNOCK', 'GETMAIL', 'GETID_SCAN']
    data = json.loads(inputJSON)
    eventType = str(data[u'event'])

    if eventType in phoneGetEvents:
        userID = str(data[u'userid'])
        option = int(data[u'option'])
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
