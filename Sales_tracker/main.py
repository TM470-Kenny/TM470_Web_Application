from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from db import db
from forms import SalesForm, ProductsForm, HoursForm, TargetForm, LoginForm, UsersForm
import os

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
            # new user created - hours initially set to 0
            new_user = Users(username, firstname.title(), lastname.title(), "password", email, admin, store_id, 0)
            db.session.add(new_user)
            db.session.commit()
            calc_targets()
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
    return render_template("users.html", users_form=users_form, all_users=all_users)


@app.route('/_getuser', methods=['POST'])
def get_user():
    user = Users.query.filter_by(id=request.get_json()["id"]).first()
    return jsonify({"firstname": user.firstname, "lastname": user.lastname, "email": user.email, "admin": user.admin, "store": user.store_id})


# route for deleting selected user
@app.route('/<int:user_id>/delete_user/', methods=["POST"])
def delete_user(user_id):
    Users.query.filter_by(id=user_id).delete()
    # when the user is deleted the target linked to the user is deleted and targets are then recalculated
    Targets.query.filter_by(username=user_id).delete()
    db.session.commit()
    calc_targets()
    return redirect(url_for("users"))


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
def get_product():
    product = Products.query.filter_by(id=request.get_json()["id"]).first()
    return jsonify({"device": product.device, "data": product.data, "length": product.length, "price": round(product.price, 2), "revenue": round(product.revenue, 2), "commission": round(product.commission, 2)})


@app.route('/<int:product_id>/delete_product/', methods=["POST"])
def delete_product(product_id):
    Products.query.filter_by(id=product_id).delete()
    db.session.commit()
    return redirect(url_for("database"))


# route for targets page
@app.route('/targets/', methods=['GET', 'POST'])
def targets():
    target_form = TargetForm()
    hours_form = HoursForm()
    store_targets = StoreTargets.query.all()
    user_targets = Targets.query.all()
    choices = [""]
    hours_form.username.choices = choices + [row.username for row in Users.query.all()]
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
        store_users = Users.query.filter_by(store_id=store.id).all()
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
def sales():
    all_sales = Sales.query.all()

    sales_form = SalesForm(form_name='Sales Form')
    # blank default value
    choices = [""]
    # set comprehension for unique values converted to list
    sales_form.username.choices = choices + [row.username for row in Users.query.all()]
    sales_form.device_name.choices = choices + list({row.device for row in Products.query.all()})
    sales_form.data_amount.choices = choices + list({row.data for row in Products.query.all()})
    sales_form.contract_length.choices = choices + list({row.length for row in Products.query.all()})
    sales_form.price.choices = choices + list({round(row.price,2) for row in Products.query.all()})
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
        product_id = Products.query.filter(db.and_(Products.device == device, Products.data == data,
                                                   Products.length == length, Products.price == price)).first().id

        # find the user if in users table from username input in form
        user = Users.query.filter_by(username=username).first().id
        if sales_form.sale_id.data == "":
            new_sale = Sales(user, new, product_id, discount, insurance)
            db.session.add(new_sale)
            db.session.commit()
            update_progress(new_sale)
        else:
            update_sale = Sales.query.filter_by(id=sales_form.sale_id.data).first()
            update_sale.user = user
            update_sale.new = new
            update_sale.product_id = product_id
            update_sale.discount = discount
            update_sale.insurance = insurance
            db.session.commit()
    return redirect(url_for("sales"))

@app.route('/_updatesalesdrop', methods=['POST'])
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
    device = list({row.device for row in Products.query.filter(db.and_(*filters)).all()})
    data = list({row.data for row in Products.query.filter(db.and_(*filters)).all()})
    length = list({row.length for row in Products.query.filter(db.and_(*filters)).all()})
    price = list({round(row.price,2) for row in Products.query.filter(db.and_(*filters)).all()})
    # check if all values are "" by converting to set, to remove duplicates, and checking length
    if len({request.get_json()['device'], request.get_json()['data'], request.get_json()['length'],
            request.get_json()['price']}) == 1:
        device = list({row.device for row in Products.query.all()})
        data = list({row.data for row in Products.query.all()})
        length = list({row.length for row in Products.query.all()})
        price = list({round(row.price, 2) for row in Products.query.all()})
    return jsonify({"device": device, "data": data, "length": length, "price": price})

@app.route('/_getsale', methods=['POST'])
def get_sale():
    sale = Sales.query.filter_by(id=request.get_json()["id"]).first()
    user = Users.query.filter_by(id=sale.user).first()
    product = Products.query.filter_by(id=sale.product_id).first()
    return jsonify({"username": user.username, "new": sale.new, "device": product.device, "data": product.data, "length": product.length, "price": round(product.price, 2), "discount": sale.discount, "insurance": sale.insurance})


@app.route('/<int:sale_id>/delete_sale/', methods=["POST"])
def delete_sale(sale_id):
    Sales.query.filter_by(id=sale_id).delete()
    db.session.commit()
    return redirect(url_for("sales"))

def update_progress(sale):
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

        new_progress = Progress(sale.user, new, upgrades, 0, unlimited, insurance, revenue=Products.query.filter_by(id=sale.product_id).first().revenue)
        db.session.add(new_progress)
        db.session.commit()
    else:
        user_progress = Progress.query.filter_by(username=sale.user).first()
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
        db.session.commit()
    #print(Progress.query.join(Users, ))

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

        # # reset store progress and loop through each users progress for this store
        # storeid_users = Users.query.filter_by(store_id=storeid).all()
        # update_store_progress.new = 0
        # update_store_progress.upgrades = 0
        # update_store_progress.broadband = 0
        # update_store_progress.unlimited = 0
        # update_store_progress.insurance = 0
        # update_store_progress.revenue = 0
        # for progress in [Progress.query.filter_by(username=user.id).first() for user in storeid_users]:
        #     update_store_progress.new += progress.new
        #     update_store_progress.upgrades += progress.upgrades
        #     update_store_progress.broadband += progress.broadband
        #     update_store_progress.unlimited += progress.unlimited
        #     update_store_progress.insurance += progress.insurance
        #     update_store_progress.revenue += progress.revenue
        #     db.session.commit()


if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)

