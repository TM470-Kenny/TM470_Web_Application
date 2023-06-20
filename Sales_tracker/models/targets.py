from db import db


class StoreTargets(db.Model):

    __tablename__ = 'store_targets'

    id = db.Column(db.Integer, primary_key=True)
    new = db.Column(db.Integer, nullable=False)
    upgrades = db.Column(db.Integer, nullable=False)
    broadband = db.Column(db.Integer, nullable=False)
    unlimited = db.Column(db.Integer, nullable=False)
    insurance = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Numeric, nullable=False)

    ind_targets = db.relationship('Targets', backref='store_targets', lazy='dynamic')
    store_progress = db.relationship('StoreProgress', backref='store_progress', uselist=False)

    def __init__(self, id, new, upgrades, broadband, unlimited, insurance, revenue):
        self.id = id
        self.new = new
        self.upgrades = upgrades
        self.broadband = broadband
        self.unlimited = unlimited
        self.insurance = insurance
        self.revenue = revenue

    def __repr__(self):
        return f'Store {self.id} has target new:{self.new}, upgrades: {self.upgrades}, broadband: {self.broadband}' \
               f', unlimited: {self.unlimited}, insurance: {self.insurance}, revenue: {self.revenue}'


class Targets(db.Model):

    __tablename__ = 'targets'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store_targets.id'), nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    new = db.Column(db.Integer, nullable=False)
    upgrades = db.Column(db.Integer, nullable=False)
    broadband = db.Column(db.Integer, nullable=False)
    unlimited = db.Column(db.Integer, nullable=False)
    insurance = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Numeric, nullable=False)

    user_progress = db.relationship('Progress', backref='user_progress', uselist=False)

    def __init__(self, store_id, username, new, upgrades, broadband, unlimited, insurance, revenue):
        self.store_id = store_id
        self.username = username
        self.new = new
        self.upgrades = upgrades
        self.broadband = broadband
        self.unlimited = unlimited
        self.insurance = insurance
        self.revenue = revenue

    def __repr__(self):
        return f'User {self.username} has target new:{self.new}, upgrades: {self.upgrades}, broadband: {self.broadband}' \
               f', unlimited: {self.unlimited}, insurance: {self.insurance}, revenue: {self.revenue}'


class Progress(db.Model):

    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, db.ForeignKey('targets.username'), nullable=False, unique=True)
    new = db.Column(db.Integer, nullable=False)
    upgrades = db.Column(db.Integer, nullable=False)
    broadband = db.Column(db.Integer, nullable=False)
    unlimited = db.Column(db.Integer, nullable=False)
    insurance = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Numeric, nullable=False)
    commission  = db.Column(db.Numeric, nullable=False)

    def __init__(self, username, new, upgrades, broadband, unlimited, insurance, revenue, commission):
        self.username = username
        self.new = new
        self.upgrades = upgrades
        self.broadband = broadband
        self.unlimited = unlimited
        self.insurance = insurance
        self.revenue = revenue
        self.commission = commission

    def __repr__(self):
        return f'User {self.username} has sold new:{self.new}, upgrades: {self.upgrades}, broadband: {self.broadband}' \
               f', unlimited: {self.unlimited}, insurance: {self.insurance}, revenue: {self.revenue}'


class StoreProgress(db.Model):

    __tablename__ = 'store_progress'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store_targets.id'), nullable=False)
    new = db.Column(db.Integer, nullable=False)
    upgrades = db.Column(db.Integer, nullable=False)
    broadband = db.Column(db.Integer, nullable=False)
    unlimited = db.Column(db.Integer, nullable=False)
    insurance = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Numeric, nullable=False)

    def __init__(self, store_id, new, upgrades, broadband, unlimited, insurance, revenue):
        self.store_id = store_id
        self.new = new
        self.upgrades = upgrades
        self.broadband = broadband
        self.unlimited = unlimited
        self.insurance = insurance
        self.revenue = revenue

    def __repr__(self):
        return f'Store {self.store_id} has sold new:{self.new}, upgrades: {self.upgrades}, broadband: {self.broadband}' \
               f', unlimited: {self.unlimited}, insurance: {self.insurance}, revenue: {self.revenue}'