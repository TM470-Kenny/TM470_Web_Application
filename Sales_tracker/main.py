import flask_login
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, abort
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from db import db
from forms import SalesForm, ProductsForm, HoursForm, TargetForm, LoginForm, UsersForm
import os
import secrets
import string
from werkzeug.security import generate_password_hash
from decimal import Decimal

from models.products import Products
from models.sales import Sales
from models.targets import StoreTargets, Targets, Progress, StoreProgress
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

# instantiate the login manager
lm = LoginManager()
# set redirect url for unauthorised users
lm.login_view = "/"
lm.init_app(app)


@lm.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()


# decorator function to check user is admin before granting access
def permission_required(user):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not user.admin:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(current_user)(f)


# decorator to remove access if user is deleted
def required(user):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if user.is_deleted:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def active_required(f):
    return required(current_user)(f)


# basic route for login page - linking to html file
@app.route('/', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data.lower()
        password = login_form.password.data

        user = Users.query.filter_by(username=username).first()

        # check password matches if user exists
        if user:
            if user.verify_password(password):
                if not user.is_deleted:
                    login_user(user)
                    if user.admin:
                        return redirect(url_for('users'))
                    else:
                        return redirect(url_for('targets'))
                else:
                    flash("Inactive account")
                # delete cookies after 1 hour to reset user login
                app.config['PERMANENT_SESSION_LIFETIME'] = 3600
            else:
                flash("Incorrect password")
        # alert user if username does not exist
        else:
            flash("Username invalid")
    return render_template("login.html", login_form=login_form)


# route for logging out users back to login page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully logged out")
    return redirect(url_for('login'))

# route for users page
@app.route('/users/', methods=['GET', 'POST'])
@login_required
@active_required
@admin_required
def users():
    users_form = UsersForm()
    all_users = Users.query.filter_by(is_deleted=False).all()
    if users_form.validate_on_submit():
        firstname = users_form.firstname.data
        lastname = users_form.lastname.data
        email = users_form.email.data
        admin = users_form.admin.data
        store_id = users_form.store_id.data
        if users_form.user_id.data == "":
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
            # Create alphabet of accepted password characters
            letters = string.ascii_letters
            nums = string.digits
            special = string.punctuation
            alphabet = letters + nums + special
            passw = ''
            # generate password of 10 characters using specified alphabet and secrets module
            for i in range(10):
                passw += ''.join(secrets.choice(alphabet))
            # password is hashed before being stored in the database
            hash_p = generate_password_hash(passw)
            # new user created - hours initially set to 0
            new_user = Users(username, firstname.title(), lastname.title(), hash_p, email, admin, store_id, 0)
            db.session.add(new_user)
            db.session.commit()
            calc_targets()
            # display temp password on users page
            flash(passw)
        else:
            # Find entry using user id in hidden field
            update_user = Users.query.filter_by(id=users_form.user_id.data).first()
            update_user.firstname = firstname
            update_user.lastname = lastname
            update_user.email = email
            update_user.admin = admin
            # if the store id is changed then remove the target linked to this user
            if update_user.store_id != store_id:
                Targets.query.filter_by(username=update_user.id).delete()
            update_user.store_id = store_id
            db.session.commit()
            # recalculate user targets
            calc_targets()
        return redirect(url_for("users"))
    return render_template("users.html", users_form=users_form, all_users=all_users, admin=flask_login.current_user.admin)


@app.route('/_getuser', methods=['POST'])
@login_required
@active_required
def get_user():
    user = Users.query.filter_by(id=request.get_json()["id"]).first()
    return jsonify({"firstname": user.firstname, "lastname": user.lastname, "email": user.email, "admin": user.admin, "store": user.store_id})


# route for deleting selected user
@app.route('/<int:user_id>/delete_user/', methods=["POST"])
@login_required
@active_required
@admin_required
def delete_user(user_id):
    Users.query.filter_by(id=user_id).first().is_deleted = True
    # when the user is deleted the target linked to the user is deleted and targets are then recalculated
    Targets.query.filter_by(username=user_id).delete()
    db.session.commit()
    calc_targets()
    return redirect(url_for("users"))


# route for database page
@app.route('/database/', methods=['GET', 'POST'])
@login_required
@active_required
@admin_required
def database():
    products_form = ProductsForm()
    all_products = Products.query.filter_by(is_deleted=False).all()
    if products_form.validate_on_submit():
        device = products_form.device_name.data
        data = products_form.data_amount.data
        length = products_form.contract_length.data
        price = products_form.price.data
        revenue = products_form.revenue.data
        commission = products_form.commission.data
        if products_form.product_id.data == "":
            new_product = Products(device, data, length, price, revenue, commission)
            db.session.add(new_product)
            db.session.commit()
        else:
            update_product = Products.query.filter_by(id=products_form.product_id.data).first()
            update_product.device = device
            update_product.data = data
            update_product.length = length
            update_product.price = price
            update_product.revenue = revenue
            update_product.commission = commission
            db.session.commit()
        return redirect(url_for("database"))
    return render_template("database.html", products_form=products_form, all_products=all_products)


@app.route('/_getproduct', methods=['POST'])
@login_required
@active_required
def get_product():
    product = Products.query.filter_by(id=request.get_json()["id"]).first()
    return jsonify({"device": product.device, "data": product.data, "length": product.length, "price": round(product.price, 2), "revenue": round(product.revenue, 2), "commission": round(product.commission, 2)})


@app.route('/<int:product_id>/delete_product/', methods=["POST"])
@login_required
@active_required
@admin_required
def delete_product(product_id):
    Products.query.filter_by(id=product_id).first().is_deleted = True
    db.session.commit()
    return redirect(url_for("database"))


# route for targets page
@app.route('/targets/', methods=['GET', 'POST'])
@login_required
@active_required
def targets():
    target_form = TargetForm()
    hours_form = HoursForm()
    store_targets = StoreTargets.query.all()
    # order targets table by users username
    user_targets = Targets.query.join(Users).order_by(Users.username).all()
    # get target linked to current user and move to the front of list of targets to be displayed first
    current_target = ""
    for target in user_targets:
        if target.username == current_user.id:
            current_target = target
    if current_target != "":
        user_targets.remove(current_target)
        user_targets.insert(0, current_target)

    choices = [""]
    hours_form.username.choices = choices + [row.username for row in Users.query.filter_by(store_id=current_user.store_id, is_deleted=False).all()]
    if target_form.validate_on_submit():
        id = current_user.store_id
        new = target_form.new.data
        upgrades = target_form.upgrades.data
        broadband = target_form.broadband.data
        unlimited = target_form.unlimited.data
        insurance = target_form.new.data
        revenue = target_form.revenue.data
        # update target if current user target exists for corresponding store id
        if StoreTargets.query.filter_by(id=current_user.store_id).first():
            update_target = StoreTargets.query.filter_by(id=current_user.store_id).first()
            update_target.new = new
            update_target.upgrades = upgrades
            update_target.broadband = broadband
            update_target.unlimited = unlimited
            update_target.insurance = insurance
            update_target.revenue = revenue
        # else create new target
        else:
            new_target = StoreTargets(id, new, upgrades, broadband, unlimited, insurance, revenue)
            db.session.add(new_target)
        db.session.commit()
        calc_targets()
        return redirect(url_for("targets"))
    if hours_form.validate_on_submit():
        # NEED TO EDIT EXISTING USER - UPDATE THE SELECTED USERS NUM HOURS INPUT
        update_user = Users.query.filter_by(username=hours_form.username.data).first()
        update_user.hours_working = hours_form.hours.data
        db.session.commit()
        calc_targets()
        return redirect(url_for("targets"))
    return render_template("targets.html", hours_form=hours_form, target_form=target_form, store_targets=store_targets,
                           user_targets=user_targets)


def calc_targets():
    store_targets = StoreTargets.query.all()
    user_targets = Targets.query.all()
    # for each store id
    for store in store_targets:
        total_hours = 0
        store_users = Users.query.filter_by(store_id=store.id, is_deleted=False).all()
        for user in store_users:
            # calculate total num hours
            total_hours += user.hours_working
        if total_hours > 0:
            for user in store_users:
                # divide targets by total num hours * current users hours
                new = round((store.new / total_hours) * user.hours_working, 0)
                upgrades = round((store.upgrades / total_hours) * user.hours_working, 0)
                broadband = round((store.broadband / total_hours) * user.hours_working, 0)
                unlimited = round((store.unlimited / total_hours) * user.hours_working, 0)
                insurance = round((store.insurance / total_hours) * user.hours_working, 0)
                revenue = round((store.revenue / total_hours) * user.hours_working, 2)
                # creating list of usernames to compare against usernames in targets table
                names = [Users.query.filter_by(id=name.username).first().username for name in user_targets]
                # if user exists in targets table
                if user.username in names:
                    # update results in existing user target
                    update_target = Targets.query.filter_by(username=user.id).first()
                    update_target.new = new
                    update_target.upgrades = upgrades
                    update_target.broadband = broadband
                    update_target.unlimited = unlimited
                    update_target.insurance = insurance
                    update_target.revenue = revenue
                    db.session.commit()
                else:
                    # add results to new target entry
                    new_target = Targets(store.id, user.id, new, upgrades, broadband, unlimited, insurance, revenue)
                    db.session.add(new_target)
                    db.session.commit()


# route for sales tracker page
@app.route('/sales/', methods=['GET', 'POST'])
@login_required
@active_required
def sales():
    all_sales = Sales.query.all()

    sales_form = SalesForm(form_name='Sales Form')
    # blank default value
    choices = [""]
    # set comprehension for unique values converted to list
    # if admin, show usernames for those with same store id
    if current_user.admin:
        sales_form.username.choices = choices + [row.username for row in Users.query.filter_by(store_id=current_user.store_id, is_deleted=False).all()]
    # if not admin only show own username
    else:
        sales_form.username.choices = choices + [current_user.username]
    sales_form.device_name.choices = choices + list({row.device for row in Products.query.filter_by(is_deleted=False).all()})
    sales_form.data_amount.choices = choices + list({row.data for row in Products.query.filter_by(is_deleted=False).all()})
    sales_form.contract_length.choices = choices + list({row.length for row in Products.query.filter_by(is_deleted=False).all()})
    sales_form.price.choices = choices + list({round(row.price, 2) for row in Products.query.filter_by(is_deleted=False).all()})
    if request.method == "GET":
        return render_template("sales.html", sales_form=sales_form, all_sales=all_sales)
    if sales_form.validate_on_submit():
        username = sales_form.username.data
        new = sales_form.new_up.data
        sale_type = sales_form.sale_type.data
        device = sales_form.device_name.data
        data = sales_form.data_amount.data
        length = sales_form.contract_length.data
        price = sales_form.price.data
        discount = 0 if sales_form.discount.data is None else sales_form.discount.data
        insurance = sales_form.insurance.data
        broadband = sales_form.broadband.data
        # find the product id in products table from details input in form
        product = Products.query.filter(db.and_(Products.device == device, Products.data == data,
                                                Products.length == length, Products.price == price)).first()
        product_id = product.id
        commission = product.commission
        # find the user if in users table from username input in form
        user = Users.query.filter_by(username=username).first().id
        if sales_form.sale_id.data == "":
            new_sale = Sales(user, new, product_id, discount, insurance, commission)
            new_sale.commission = calc_commission(new_sale)
            db.session.add(new_sale)
            db.session.commit()
            update_progress("add", new_sale)
        else:
            update_sale = Sales.query.filter_by(id=sales_form.sale_id.data).first()
            update_progress("delete", update_sale)
            update_sale.user = user
            update_sale.new = new
            update_sale.product_id = product_id
            update_sale.discount = discount
            update_sale.insurance = insurance
            update_sale.commission = calc_commission(update_sale)
            update_progress("add", update_sale)
            db.session.commit()
    return redirect(url_for("sales"))

@app.route('/_updatesalesdrop', methods=['POST'])
@login_required
@active_required
def update_sales_drop():
    filters = list()
    # append the filter for the form field if it is not empty
    if request.get_json()['device'] != "":
        filters.append(Products.device == request.get_json()['device'])
    if request.get_json()['data'] != "":
        filters.append(Products.data == request.get_json()['data'])
    if request.get_json()['length'] != "":
        filters.append(Products.length == request.get_json()['length'])
    if request.get_json()['price'] != "":
        filters.append(Products.price == request.get_json()['price'])
    # unpack the list to filter the query
    device = list({row.device for row in Products.query.filter(db.and_(*filters)).all() if not row.is_deleted})
    data = list({row.data for row in Products.query.filter(db.and_(*filters)).all() if not row.is_deleted})
    length = list({row.length for row in Products.query.filter(db.and_(*filters)).all() if not row.is_deleted})
    price = list({round(row.price,2) for row in Products.query.filter(db.and_(*filters)).all() if not row.is_deleted})
    # check if all values are "" by converting to set, to remove duplicates, and checking length
    if len({request.get_json()['device'], request.get_json()['data'], request.get_json()['length'],
            request.get_json()['price']}) == 1:
        device = list({row.device for row in Products.query.filter_by(is_deleted=False).all()})
        data = list({row.data for row in Products.query.filter_by(is_deleted=False).all()})
        length = list({row.length for row in Products.query.filter_by(is_deleted=False).all()})
        price = list({round(row.price, 2) for row in Products.query.filter_by(is_deleted=False).all()})
    return jsonify({"device": device, "data": data, "length": length, "price": price})

@app.route('/_getsale', methods=['POST'])
@login_required
@active_required
def get_sale():
    sale = Sales.query.filter_by(id=request.get_json()["id"]).first()
    user = Users.query.filter_by(id=sale.user).first()
    product = Products.query.filter_by(id=sale.product_id).first()
    return jsonify({"username": user.username, "new": sale.new, "device": product.device, "data": product.data, "length": product.length, "price": round(product.price, 2), "discount": sale.discount, "insurance": sale.insurance})


@app.route('/<int:sale_id>/delete_sale/', methods=["POST"])
@login_required
@active_required
@admin_required
def delete_sale(sale_id):
    deleted_sale = Sales.query.filter_by(id=sale_id).first()
    update_progress("delete", deleted_sale)
    Sales.query.filter_by(id=sale_id).delete()
    db.session.commit()
    return redirect(url_for("sales"))


def calc_commission(sale):
    product = Products.query.filter_by(id=sale.product_id).first()
    commission_calc = product.commission
    if sale.new:
        commission_calc += 1
    if product.data == 999:
        commission_calc += 2
    if product.length == 36:
        commission_calc += 1
    if sale.insurance != "None":
        commission_calc += 1
    if sale.discount != 0:
        commission_calc = commission_calc - (commission_calc * (Decimal(sale.discount) / 100))
    return commission_calc

def update_progress(sale_func, sale):
    # if user has not made a sale yet
    if Progress.query.filter_by(username=sale.user).first() is None:
        # if new add 1 to new
        if sale.new:
            new = 1
            upgrades = 0
        # else add 1 to upgrades
        else:
            new = 0
            upgrades = 1
        # if data = 999 (unlimited) add 1 to unlimited
        if Products.query.filter_by(id=sale.product_id).first().data == 999:
            unlimited = 1
        else:
            unlimited = 0
        # if insurance = NONE dont add
        if sale.insurance == "None":
            insurance = 0
        # else add 1 to insurance
        else:
            insurance = 1

        new_progress = Progress(sale.user, new, upgrades, 0, unlimited, insurance, Products.query.filter_by(id=sale.product_id).first().revenue, sale.commission)
        db.session.add(new_progress)
        db.session.commit()
    # if user has made a sale
    else:
        user_progress = Progress.query.filter_by(username=sale.user).first()
        # if sale is being deleted, remove from progress where required
        if sale_func == "delete":
            if sale.new:
                user_progress.new -= 1
            else:
                user_progress.upgrades -= 1
            if Products.query.filter_by(id=sale.product_id).first().data == 999:
                user_progress.unlimited -= 1
            if sale.insurance != "None":
                user_progress.insurance -= 1
            user_progress.revenue -= Products.query.filter_by(id=sale.product_id).first().revenue
            user_progress.commission -= sale.commission
        # if sale is being added, add to progress where required
        if sale_func == "add":
            if sale.new:
                user_progress.new += 1
            # else add 1 to upgrades
            else:
                user_progress.upgrades += 1
            # if data = 999 (unlimited) add 1 to unlimited
            if Products.query.filter_by(id=sale.product_id).first().data == 999:
                user_progress.unlimited += 1
            # if insurance = NONE dont add
            if sale.insurance != "None":
                user_progress.insurance += 1

            user_progress.revenue += Products.query.filter_by(id=sale.product_id).first().revenue
            user_progress.commission += sale.commission
        db.session.commit()


    # if no target add new store progress from first sale
    if StoreProgress.query.filter_by(store_id=Users.query.filter_by(id=sale.user).first().store_id).first() is None:
        new_store_progress = StoreProgress(Users.query.filter_by(id=sale.user).first().store_id, new, upgrades, 0, unlimited, insurance,
                                revenue=Products.query.filter_by(id=sale.product_id).first().revenue)
        db.session.add(new_store_progress)
        db.session.commit()
    # if target then sum columns in progress table and update store progress
    else:
        storeid = Users.query.filter_by(id=sale.user).first().store_id
        update_store_progress = StoreProgress.query.filter_by(store_id=storeid).first()
        # if sale is being deleted, remove from progress where required
        if sale_func == "delete":
            if sale.new:
                update_store_progress.new -= 1
            else:
                update_store_progress.upgrades -= 1
            if Products.query.filter_by(id=sale.product_id).first().data == 999:
                update_store_progress.unlimited -= 1
            if sale.insurance != "None":
                update_store_progress.insurance -= 1
            update_store_progress.revenue -= Products.query.filter_by(id=sale.product_id).first().revenue
        if sale_func == "add":
            if sale.new:
                update_store_progress.new += 1
            # else add 1 to upgrades
            else:
                update_store_progress.upgrades += 1
            # if data = 999 (unlimited) add 1 to unlimited
            if Products.query.filter_by(id=sale.product_id).first().data == 999:
                update_store_progress.unlimited += 1
            # if insurance = NONE dont add
            if sale.insurance != "None":
                update_store_progress.insurance += 1

            update_store_progress.revenue += Products.query.filter_by(id=sale.product_id).first().revenue

        db.session.commit()

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)

