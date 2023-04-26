from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from db import db
from forms import SalesForm, ProductsForm, HoursForm, TargetForm, LoginForm, UsersForm
import os

from models.products import Products
from models.sales import Sales
from models.targets import StoreTargets, Targets
from models.users import Users

# instantiate the Flask object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'


# finds the full path for the current directory of this file
basedir = os.path.abspath(os.path.dirname(__file__))

# connect flask app to database
# set up database location
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'sales_tracker.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

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
        username = firstname.lower()+lastname[0].lower()
        # checks if username exists, adds 1 to end until unique
        unique = False
        add = 0
        while not unique:
            if Users.query.filter_by(username=username).first():
                add = add + 1
                username = firstname.lower()+lastname[0].lower() + str(add)
            else:
                unique = True

        # ADD LOGIC TO GENERATE FIRST USE PASSWORD
        # new user created - hours initially set to 0
        new_user = Users(username, firstname.title(), lastname.title(), "password", email, admin, store_id, 0)
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
    db.init_app(app)
    app.run(port=5000, debug=True)

