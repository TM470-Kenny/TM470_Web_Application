from db import db
from werkzeug.security import check_password_hash
from flask_login import UserMixin


class Users(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(20), nullable=False, unique=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.VARCHAR(40), nullable=False, unique=True)
    admin = db.Column(db.Boolean, nullable=False)
    store_id = db.Column(db.Integer)
    hours_working = db.Column(db.Integer)
    is_deleted = db.Column(db.Boolean, default=False)

    user_sales = db.relationship('Sales', backref='users', lazy='dynamic')
    # One to One relationship for user and target/progress
    user_targets = db.relationship('Targets', backref='user_target', uselist=False)

    def __init__(self, username, firstname, lastname, password, email, admin, store_id, hours):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.email = email
        self.admin = admin
        self.store_id = store_id
        self.hours_working = hours
        self.is_deleted = False

    def __repr__(self):
        return f'{self.firstname} {self.lastname} has username: {self.username}'

# method to check the password input matches the hashed password stored in the database
    def verify_password(self, password):
        return check_password_hash(self.password, password)

