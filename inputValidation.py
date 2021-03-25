# Holds functions used for validating user input for flask app

from flask import session
from Models import User, Meeting
from flask_sqlalchemy import SQLAlchemy
import datetime


adminLogin = ['admin','password']

def has_num_and_char(givenPass):
    numNum = 0
    numChar = 0
    for char in givenPass:
        if numNum == 0 or numChar == 0:
            try:
                int(char)
                numNum += 1
            except:
                numChar += 1
        else:
            return True
    if numNum == 0 or numChar == 0:
        return False
    else:
        return True   


def validate_profile(userInput):
    passed = True
    if not 3 < len(userInput['username']) < 16:
        userInput['username'] = 'x'
        passed = False
    if not 3 < len(userInput['firstname']) < 51:
        userInput['firstname'] = 'x'
        passed = False
    if not 3 < len(userInput['lastname']) < 51:
        userInput['lastname'] = 'x'
        passed = False
    if not 3 < len(userInput['email']) < 51:
        userInput['email'] = 'x'
        passed = False
    if not 8 < len(userInput['password']) < 17 or \
       has_num_and_char(userInput['password']) == False:
        userInput['password'] = 'x'
        passed = False
    return userInput, passed


def parse_times(userInput):
    start, end = userInput['start_time'], userInput['end_time']
    times = [start, end]
    final = []
    for var in times:
        var = var.split(':')# var is now a list e.g. (['5', '30PM']
        temp = var[1].split(' ') # temp==['30','PM']
        var[1] = temp[0] # var should be ['5','30','PM']
        var.append(temp[1])
        if var[2] == 'PM':
            var[0] = str(int(var[0]) + 12)
        final.append(var)
    userInput['start_hour'], userInput['start_minute'] = final[0][0], final[0][1]
    userInput['end_hour'], userInput['end_minute'] = final[1][0], final[1][1]
    return userInput



def validate_schedule(userInput):
    passed = True
    try:
        meetingInfo = {'start_date':datetime.datetime(int(userInput['year']),
                                                      int(userInput['month']),
                                                      int(userInput['day']),
                                                      int(userInput['start_hour']),
                                                      int(userInput['start_minute'])),
                       'end_date':datetime.datetime(int(userInput['year']),
                                                    int(userInput['month']),
                                                    int(userInput['day']),
                                                    int(userInput['end_hour']),
                                                    int(userInput['end_minute']))}
    except:
        passed = False
        meetingInfo = 'invalid date'
        return meetingInfo, passed
    if meetingInfo['start_date'] >= meetingInfo['end_date']:
        passed = False
        meetingInfo = 'End time must be later than the start time'
        return meetingInfo, passed
    else:
        result = '***ALL IS WELL AND GOOD WITH THE DATES***' #Find a way to display this or confirmation on the page
        return meetingInfo, passed


def check_login(givenName, givenPass):
    global adminLogin
    if givenName == adminLogin[0] and givenPass == adminLogin[1]:
        msg = None
        return True, msg, 'admin'
    else:
        result = User.query.filter_by(username=givenName).first()
        if result == None:
            msg = 'Username not found.'
            return (False, msg, None) #(can login?, reason, user object to be logged in)
        else:
            if givenPass != getattr(result, 'password'):
                msg = 'Incorrect password.'
                return (False, msg, None)
            else:
                msg = 'Welcome!'
                return (True, msg, result)
