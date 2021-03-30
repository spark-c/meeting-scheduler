# Models for the SQLAlchemy database in meeting-scheduler
# Collin Sparks, cklsparks@gmail.com, https://github.com/spark-c/meeting-scheduler

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    admin_template = {
    'username': 'admin',
    'firstname': 'admin',
    'lastname': 'admin',
    'email': 'admin@site.com',
    'password': 'password123'
    }

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(20), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    meetings = db.relationship('Meeting', lazy='select', backref=db.backref('user', lazy='joined'))
    permissions = db.Column(db.String(), nullable=False)



    def __init__(self, userInfo):
        self.username = userInfo['username']
        self.firstname = userInfo['firstname']
        self.lastname = userInfo['lastname']
        self.email = userInfo['email']
        self.password = userInfo['password']
        self.meetings = []
        self.permissions = 'user'


    def __repr__(self):
        return f'<user(username:{self.username},\nfirstname:{self.firstname},\nlastname:{self.lastname},\nemail:{self.email},\npassword: {self.password})>\n'


class Meeting(db.Model):
    __tablename__ = 'meeting'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    printout = db.Column(db.String(100), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)


    def __init__(self, start_date, end_date, user):
        self.start_date = start_date
        self.end_date = end_date
        self.duration = self.end_date - self.start_date
        self.user_id = user.id
        self.printout = self.start_date.strftime('%a, %d %b %Y from %I:%M%p to ') + self.end_date.strftime('%I:%M%p')+ ' ' + f'(Duration: {self.duration})'
                                                # the above string is built from datetime placeholders
