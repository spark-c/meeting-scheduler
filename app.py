# meeting-scheduler
# Collin Sparks, cklsparks@gmail.com, https://github.com/spark-c/meeting-scheduler
# Python 3

from flask import Flask, session, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
import os
import pprint
from Models import User, Meeting, db
import inputValidation as inVa


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
print(os.environ['APP_SETTINGS']) # temporary; confirms which set of vars we're using

# app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///user.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db = SQLAlchemy(app) used to live here but was moved to Models.py
db.app = app
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)

@app.route("/home", methods=['POST','GET'])
@app.route("/", methods=['POST','GET'])
def home():
    if request.method == 'POST':
        if 'logout' in request.form:
            return redirect(url_for('logout'))
    return render_template("home.html")


@app.route("/admin", methods=['POST','GET'])
def admin():
    if session.get('permissions') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST': #if the user hit the delete button
        if 'logout' in request.form:
            return redirect(url_for('logout'))

        if 'deleteuser' in request.form:
            userList = User.query.all() #this should be identical to the one previously sent to the browser
            working = request.form.to_dict() #make it a mutable dict
            working.pop('deleteuser') #get rid of the {'delete':'Delete} at the beginning
            deleteQueue = []
            for user in working: #working is now a dict whose keys are (string) digits representing the userList indexes needing deleted
                deleteQueue.append(userList[int(user)])
            for user in deleteQueue:
                db.session.delete(user)
                userList.remove(user)
            db.session.commit()
            return redirect(url_for('admin'))

        if 'clearalluser' in request.form:
            working = User.query.all()
            working.pop('clearalluser')
            for user in working:
                db.session.delete(user)
            db.session.commit()
            session.clear()
            return redirect(url_for('admin'))

        if 'deletemeeting' in request.form:
            working = request.form.to_dict()
            working.pop('deletemeeting')
            for key in working: #the keys of the dict are the printouts of the meeting objects to be deleted
                temp = Meeting.query.filter_by(printout=key).first()
                db.session.delete(temp)
            db.session.commit()
            return redirect(url_for('admin'))

        if 'clearallmeeting' in request.form:
            allMeetings = Meeting.query.all()
            for item in allMeetings:
                db.session.delete(item)
            db.session.commit()
            return redirect(url_for('admin'))

    else:
        userList = User.query.all()
        meetingList = Meeting.query.order_by(Meeting.start_date).all()
        meetingsMaster = {}
        if len(meetingList) > 0: # if there are any meetings
            for index in meetingList:
                user = User.query.filter_by(id=index.user_id).first()
                meetingsMaster[index.printout] = f'User: {user.firstname} {user.lastname}'
                # print(meetingsMaster)
        return render_template('admin.html', userList=userList, meetingsMaster=meetingsMaster)


@app.route("/profile", methods=['POST','GET'])
def profile():
    if request.method == 'POST':
        if 'logout' in request.form:
            return redirect(url_for('logout'))
        if 'schedule' in request.form:
            return redirect(url_for('schedule'))
    if 'username' in session:
        meetingsInfo = []
        allMeetings = []
        if session.get('meeting_ids'): # and len(session['meeting_ids']) > 0: # if there are any meetings
            booked = Meeting.query.filter_by(user_id=session['user_id']).order_by(Meeting.start_date).all()
            for index in booked:
                meetingsInfo.append(index.printout)
        return render_template('profile.html', meetingsInfo=meetingsInfo)
    else:
        return redirect(url_for('login', msg=None))


@app.route("/profile/edit", methods=['POST','GET'])
def profile_edit():
    pass


@app.route("/profile/create_new", methods=['POST','GET'])
def profile_new():
    if 'username' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST': #We're going to save every entry, remove the bad ones, and replace the accepted ones in the boxes
                                #Need to check that the profile doesn't already exist
        userInput = request.form.to_dict() # request.form on it's own is an immutable dict, so we change that here
        validated, passed = inVa.validate_profile(userInput) #checks that the user input is valid
        if passed == True:
            for key in userInput:
                session[key] = userInput[key]
            print('validated: {}'.format(validated))
            user = User(validated) #Once we have an acceptable form
            db.session.add(user)
            db.session.commit()
            session['user_id'] = User.query.filter_by(username=session['username']).first().id
        else:
            return render_template('profile_new.html', validated=validated)

        return redirect(url_for('profile'))
    else:
        return render_template('profile_new.html')


@app.route('/schedule', methods=['POST','GET'])
def schedule():
    if 'username' not in session: #check logged in
        msg = 'Login required.'
        return redirect(url_for('login', msg=msg))
    if request.method == 'POST': #if form was submitted
        if 'logout' in request.form: #check if it was logout button
            return redirect(url_for('logout'))
        userInput = request.form.to_dict()
        try:
            inVa.parse_times(userInput) #try to convert the time inputs
        except:
            validated = 'invalid input'
            return render_template('schedule.html', validated=validated)
        validated, passed = inVa.validate_schedule(userInput)
        if passed == True: #if everything was valid
            userObj = User.query.filter_by(id=session['user_id']).first()
            meeting = Meeting(validated['start_date'], validated['end_date'], userObj)
            db.session.add(meeting)
            db.session.commit()
            meetingsBooked = Meeting.query.filter_by(user_id=session['user_id']).all()
            temp = []
            for obj in meetingsBooked:
                temp.append(obj.id)
            session['meeting_ids'] = temp
            return redirect(url_for('profile'))
        else:
            return render_template('schedule.html', validated=validated)
    else:
        return render_template('schedule.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if 'username' in session:
        return redirect(url_for('profile'))
    elif request.method == 'POST':
        givenName = request.form['givenName']
        givenPass = request.form['givenPass']
        logAttempt = inVa.check_login(givenName, givenPass)
        if logAttempt[0] == True: # e.g. they logged in correctly
            user = logAttempt[2] #fetches the correct User object
            if user != 'admin':
                session['username'] = user.username
                session['firstname'] = user.firstname
                session['lastname'] = user.lastname
                session['email'] = user.email
                session['password'] = user.password
                session['user_id'] = user.id
                session['meeting_ids'] = []
                session['permissions'] = user.permissions
                meetingsBooked = db.session.query(Meeting).filter_by(user_id=user.id).all()
                for obj in meetingsBooked:
                    session['meeting_ids'].append(obj.id)
                return redirect(url_for('profile'))
            else:
                session['username'] = inVa.adminLogin[0]
                session['firstname'] = 'admin'
                session['lastname'] = 'admin'
                session['email'] = 'admin@site.com'
                session['password'] = inVa.adminLogin[1]
                session['user_id'] = None
                session['meeting_ids'] = []
                return redirect(url_for('profile'))
        else:
            return render_template('login.html', msg=logAttempt[1])
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    if 'username' in session:
        session.clear()
    return redirect(url_for('home'))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
