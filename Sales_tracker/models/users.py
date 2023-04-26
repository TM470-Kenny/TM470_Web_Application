from db import db


class Users(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    admin = db.Column(db.Boolean, nullable=False)
    store_id = db.Column(db.Integer)
    hours_working = db.Column(db.Integer)

    user_sales = db.relationship('Sales', backref='users', lazy='dynamic')
    # One to One relationship for user and target
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

    def __repr__(self):
        return f'{self.firstname} {self.lastname} has username: {self.username}'
