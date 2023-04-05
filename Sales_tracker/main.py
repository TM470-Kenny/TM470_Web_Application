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
    data = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    revenue = db.Column(db.Numeric, nullable=False)
    commission = db.Column(db.Numeric, nullable=False)
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
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    new = db.Column(db.Boolean, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    discount = db.Column(db.Integer)
    insurance = db.Column(db.Text)

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
    store_id = db.Column(db.Integer, db.ForeignKey('store_targets.id'), nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    new = db.Column(db.Integer, nullable=False)
    upgrades = db.Column(db.Integer, nullable=False)
    broadband = db.Column(db.Integer, nullable=False)
    unlimited = db.Column(db.Integer, nullable=False)
    insurance = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Numeric, nullable=False)

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
@app.route('/users/', methods=['GET', 'POST'])
def users():
    users_form = UsersForm()
    all_users = Users.query.all()
    if users_form.validate_on_submit():
        firstname = users_form.firstname.data
        lastname = users_form.lastname.data
        email = users_form.email.data
        admin = users_form.admin.data
        store_id = users_form.store_id.data

        # generate username from firstname and lastname
        username = firstname+lastname[0]
        # checks if username exists, adds 1 to end until unique
        unique = False
        add = 0
        while not unique:
            if Users.query.filter_by(username=username).first():
                add = add + 1
                username = firstname+lastname[0] + str(add)
            else:
                unique = True

        # ADD LOGIC TO GENERATE FIRST USE PASSWORD
        # new user created - hours initially set to 0
        new_user = Users(username, firstname, lastname, "password", email, admin, store_id, 0)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("users"))
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
@app.route('/targets/', methods=['GET', 'POST'])
def targets():
    target_form = TargetForm()
    hours_form = HoursForm()
    store_targets = StoreTargets.query.all()
    user_targets = Targets.query.all()
    if target_form.validate_on_submit():
        # EDIT EXISTING STORE TARGET BASED ON ADMIN LOGIN STORE ID
        # CURRENTLY ONLY ABLE TO ADD NEW TARGET WITH NEW STORE ID
        new = target_form.new.data
        upgrades = target_form.upgrades.data
        broadband = target_form.broadband.data
        unlimited = target_form.unlimited.data
        insurance = target_form.new.data
        revenue = target_form.revenue.data

        new_target = StoreTargets(new, upgrades, broadband, unlimited, insurance, revenue)
        db.session.add(new_target)
        db.session.commit()
        return redirect(url_for("targets"))
    if hours_form.validate_on_submit():
        username = hours_form.username.data

        # find the user if in users table from username input in form
        user = Users.query.filter_by(username=username).first().id

        # NEED TO EDIT EXISTING USER - UPDATE THE SELECTED USERS NUM HOURS INPUT
        # user_hours = Users()
        # db.session.add(user_hours)
        # db.session.commit()
        return redirect(url_for("targets"))
    return render_template("targets.html", hours_form=hours_form, target_form=target_form, store_targets=store_targets,
                           user_targets=user_targets)


# route for sales tracker page
@app.route('/sales/', methods=['GET', 'POST'])
def sales():
    sales_form = SalesForm()
    all_sales = Sales.query.all()
    if sales_form.validate_on_submit():
        username = sales_form.username.data
        new = sales_form.new_up.data
        sale_type = sales_form.sale_type.data
        device = sales_form.device_name.data
        data = sales_form.data_amount.data
        length = sales_form.contract_length.data
        price = sales_form.price.data
        discount = sales_form.discount.data
        insurance = sales_form.insurance.data
        broadband = sales_form.broadband.data

        # find the product id in products table from details input in form
        product_id = Products.query.filter(db.and_(Products.device == device, Products.data == data,
                                                   Products.length == length, Products.price == price)).first().id

        # find the user if in users table from username input in form
        user = Users.query.filter_by(username=username).first().id

        new_sale = Sales(user, new, product_id, discount, insurance)
        db.session.add(new_sale)
        db.session.commit()
        return redirect(url_for("sales"))
    return render_template("sales.html", sales_form=sales_form, all_sales=all_sales)


if __name__ == '__main__':
    app.run(debug=True)

