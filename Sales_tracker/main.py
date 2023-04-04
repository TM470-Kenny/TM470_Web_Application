from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5

from forms import SalesForm, ProductsForm, HoursForm, TargetForm, LoginForm, UsersForm

import os
from flask_sqlalchemy import SQLAlchemy



# instantiate the Flask object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'


# finds the full path for the current directory of this file
basedir = os.path.abspath(os.path.dirname(__file__))

# connect flask app to database
# set up database location
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'sales_tracker.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)


#####################################
class Products(db.Model):

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.Text)
    data = db.Column(db.Integer)
    length = db.Column(db.Integer)
    price = db.Column(db.Numeric)
    revenue = db.Column(db.Numeric)
    commission = db.Column(db.Numeric)
    # Set up One to Many relationship
    product_sales = db.relationship('Sales', backref='product', lazy='dynamic')

    def __init__(self, device, data, length, price, revenue, commission):
        self.device = device
        self.data = data
        self.length = length
        self.price = price
        self.revenue = revenue
        self.commission = commission

    def __repr__(self):
        return f'{self.device} with {self.data} costs {self.price}'


class Sales(db.Model):

    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    new = db.Column(db.Boolean)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    discount = db.Column(db.Integer)
    insurance = db.Column(db.Boolean)

    def __init__(self, user, new, product_id, discount, insurance):
        self.user = user
        self.new = new
        self.product_id = product_id
        self.discount = discount
        self.insurance = insurance

    def __repr__(self):
        return f'{self.user} sold product id {self.product_id} with {self.discount}% discount'

class Users(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)
    password = db.Column(db.Text)
    admin = db.Column(db.Boolean)
    store_id = db.Column(db.Integer)

    user_sales = db.relationship('Sales', backref='users', lazy='dynamic')

    def __init__(self,username,firstname,lastname,password,admin,store_id):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.admin = admin
        self.store_id = store_id

    def __repr__(self):
        return f'{self.firstname} {self.lastname} has username: {self.username}'


class StoreTargets(db.Model):

    __tablename__ = 'store_targets'

    id = db.Column(db.Integer, primary_key=True)
    new = db.Column(db.Integer)
    upgrades = db.Column(db.Integer)
    broadband = db.Column(db.Integer)
    unlimited = db.Column(db.Integer)
    insurance = db.Column(db.Integer)
    revenue = db.Column(db.Numeric)

    ind_targets = db.relationship('Targets', backref='store_targets', lazy='dynamic')

    def __init__(self, new, upgrades, broadband, unlimited, insurance, revenue):
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
    store_id = db.Column(db.Integer, db.ForeignKey('store_targets.id'))
    username = db.Column(db.Integer)
    new = db.Column(db.Integer)
    upgrades = db.Column(db.Integer)
    broadband = db.Column(db.Integer)
    unlimited = db.Column(db.Integer)
    insurance = db.Column(db.Integer)
    revenue = db.Column(db.Numeric)

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


######################################

# instantiate bootstrap to be used with form
bootstrap = Bootstrap5(app)




# basic route for login page - linking to html file
@app.route('/')
def login():
    login_form = LoginForm()
    return render_template("login.html", login_form=login_form)


# route for users page
@app.route('/users/')
def users():
    users_form = UsersForm()
    all_users = Users.query.all()
    return render_template("users.html", users_form=users_form, all_users=all_users)


# route for database page
@app.route('/database/', methods=['GET', 'POST'])
def database():
    products_form = ProductsForm()
    all_products = Products.query.all()
    if products_form.validate_on_submit():
        device = products_form.device_name.data
        data = products_form.data_amount.data
        length = products_form.contract_length.data
        price = products_form.price.data
        revenue = products_form.revenue.data
        commission = products_form.commission.data

        new_product = Products(device, data, length, price, revenue, commission)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("database"))
    return render_template("database.html", products_form=products_form, all_products=all_products)


# route for targets page
@app.route('/targets/')
def targets():
    target_form = TargetForm()
    hours_form = HoursForm()
    store_targets = StoreTargets.query.all()
    user_targets = Targets.query.all()
    return render_template("targets.html", hours_form=hours_form, target_form=target_form, store_targets=store_targets,
                           user_targets=user_targets)


# route for sales tracker page
@app.route('/sales/', methods=['GET', 'POST'])
def sales():
    sales_form = SalesForm()
    all_sales = Sales.query.all()
    all_products = Products.query.all()
    return render_template("sales.html", sales_form=sales_form, all_sales=all_sales, all_products=all_products)


if __name__ == '__main__':
    app.run(debug=True)

