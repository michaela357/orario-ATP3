# Define a User table schema
from extensions import db
from flask_login import UserMixin
from datetime import date

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=True)
    quote = db.Column(db.String(250), nullable=True)
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    #constructor method
    def __init__(self, email, name, password, quote): 
        self.email = email
        self.name = name
        self.password = password
        self.quote = quote

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    due_date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(200), nullable=False)
    complete = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, due_date, description, complete, user_id):
        self.due_date = due_date
        self.description = description
        self.complete = complete
        self.user_id = user_id

    def to_dict(self):
        return {
            'id': self.id,
            'due_date': self.due_date.strftime('%Y-%m-%d'),
            'description': self.description,
            'complete': self.complete
        }      