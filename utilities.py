'''
Arthur Verkaik
s1247563
Utility functions for the server
# TODO
  - REFACTOR REFACTOR REFACTOR.
  - Documentation for each function
  - testing functions
  - return appropriate HTTP codes instead of 200 for everything.
  - throw/catch errors
  - standardize queries
'''

import json, uuid
from passlib.hash import pbkdf2_sha256
from server import db, Users, Connections, Events, Raspberries

'''
Function: _commitChange
Input: newRow - this is a new entry in a table staged for commit.
       noError - Boolean which is used to check whether change has been successfully
                 committed or not.
Output: Boolean which shows whether change has been successfully committed or not.
'''

def _commitChange(newRow, noError):
    try:
        db.session.add(newRow)
        db.session.commit()
    except:
        db.session.rollback()
        noError = False
        raise

    return noError

'''
Function: checkUser
Input: username - string, and email - string (self-explanatory inputs).
Output: Checks the given username and email against the database and returns
a boolean. (True = user exists.)
'''

def checkUser(username, email):
    if len(Users.query.filter_by(email=email).all()) == 0 and len(Users.query.filter_by(username=username).all()) == 0:
        return True
    else:
        return False


'''
Function: addUser
Input: username, email, firstName, lastName, password (all strings, self-explanatory)
Output: Adds a user with the given details to the database if no constraints are broken.
If the addition has been succesful, the function returns the newly added user's uuid.
If the operation failed, the function returns false.
'''

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

'''
Function: addRaspberry
Input: raspberryID - a UUID in string format.
Output: Adds a raspberry to the Raspberries table, if no constraints are broken.
Returns the newly added pi's UUID if the operation was successful, otherwise,
returns False.
'''

def addRaspberry(raspberryID):
    existingPis = Raspberries.query.filter_by(raspberryid=raspberryID).all()
    if (len(existingPis) == 0):
        newRaspberry = Raspberries(raspberryid=raspberryID)
        _commitChange(newRaspberry, True)
        newRaspberryID = Raspberries.query.filter_by(raspberryid=raspberryID).first()
        return newRaspberryID.raspberryid
    else:
        return False


'''
Function: connectUserToRaspberry
Input: userID, raspberryID (both UUIDs), raspberryName (string)
Output: Adds a new entry in Connections which links the specified user and raspberry
together. The name given as input is stored in the raspberryname column. The output
is a boolean. If the data was successfully added, return True. Otherwise return False.
'''

def connectUserToRaspberry(userID, raspberryID, raspberryName):

    raspberry = Raspberries.query.filter(Raspberries.raspberryid==raspberryID).first()

    if raspberry != None:
        newConnection = Connections(raspberryid=raspberryID, userid=userID, raspberryname=raspberryName)
        db.session.add(newConnection)
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            raise
    else:
        return False

'''
Function: addEvent
Input: raspberryID (UUID), eventType, eventTime, note, name (strings)
Output: Adds an event if a replica doesn't already exist. If a replica exists, return
False. Otherwise, return true.
'''
def addEvent(raspberryID, eventType, eventTime, note, name):
    if (len(db.session.query(Events).filter(Events.raspberryid==raspberryID).\
            filter(Events.eventtype==eventType).filter(Events.eventtime==eventTime).\
            all()) > 0):
        return False

    newEvent = Events(raspberryid=raspberryID, eventtype=eventType, eventtime=eventTime, note=note, name=name)
    return _commitChange(newEvent, True)

# Deals with pi POST requests. Returns a boolean (True = successfully added)
'''
Function: piPosts
Input: data (json), eventType (string)
Output: adds an event to the database with the given data. Returns the Output
of addEvent (true if event added, false otherwise).
'''
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
'''
Function: phonePosts
Input: data (json), eventType (string)
Output: If the event is register, returns the output of addUser with the given
data. If the event is adding a pi, returns the output of connectUserToRaspberry.
'''
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

'''
The function which deals with any kind of post (from phone or pi)
Function: postJSON
Input: inputJSON (json object)
Output: the output of the appropriate post function (if the request is from
a phone, use phonePosts, if from a pi, use piPosts).
'''

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

'''
Function: getEvents
Input: eventType (string), userID (UUID), option (binary number)
Output: returns a list of events. The query which gets these events is determined
by the inputs. Supports ALL, UNSENT, and GETKNOCK/MAIL/ID_SCAN.
'''
def getEvents(eventType, userID, option):
    events = []
    eventsBaseQuery = db.session.query(Events).filter(Users.userid==userID).\
                 filter(Users.userid==Connections.userid).\
                 filter(Connections.raspberryid==Events.raspberryid)
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

'''
Function: phoneGets
Input: events (list of events)
Output: a json containing one object. This object is a list of all the events in
the input, and will be sent to the phone.
'''

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

'''
Function: getPies
Input: userID (UUID)
Output: Returns the list of raspberries connected to the specified user.
'''

def getPies(userID):
    raspberryList = []
    connectedPis = Connections.query.filter(Connections.userid==userID).all()
    for i in connectedPis:
        raspberryRow = Raspberries.query.filter(Raspberries.raspberryid==i.raspberryid).first()
        raspberry = {"raspberryID":i.raspberryid, "raspberryName":i.raspberryname}
        raspberryList.append(raspberry)
    return raspberryList

'''
Function: checkLogin
Input: userID (string), password(string)
Output: boolean. if the given details match the stored details, return True. Otherwise,
return False.
'''
def checkLogin(userID, password):
    hashedPassword =  Users.query.filter_by(userid=userID).with_entities(Users.password).first()
    return pbkdf2_sha256.verify(password, hashedPassword.password)

'''
Function: getJSON
Input: inputJSON (json object)
Output: This is the function that deals with GET requests. Depending on the event type,
we know which device has sent the request. We then use the appropriate functions to
determine the output of the function, a json with all the information the phone/pi
needs.
'''
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
