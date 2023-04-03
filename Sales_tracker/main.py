from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_bootstrap import Bootstrap5

import sqlite3


# instantiate the Flask object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

# create connection to the database
def connect_db():
    conn = sqlite3.connect('sales_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn


# instantiate bootstrap to be used with form
bootstrap = Bootstrap5(app)

# form design for sales tracker form
class SalesForm(FlaskForm):
    # set as current logged in user - admin can change
    username = StringField('Username:', validators=[DataRequired()])
    new_up = RadioField('New or Upgrade:', choices=['New', 'Upgrade'])
    sale_type = SelectField('Sale Type:', choices=['Device', 'Sim', 'Broadband'])
    # visible upon choosing device
    device_name = StringField('Device Name:')
    data_amount = SelectField('Data Amount:', choices=['1GB', '5GB', '100GB', 'Unlimited'])
    contract_length = SelectField('Contract Length:', choices=['1m', '12m', '24m'])
    # price dependent on data and device selected
    price = SelectField('Price:', choices=['£10.00', '£14.00', '£20.00', '£35.00'])
    discount = IntegerField('Discount:', validators=[NumberRange(min=0, max=100)])
    # visible upon choosing device
    insurance = SelectField('Insurance:', choices=['None', 'Tier 1 Damage', 'Tier 1 Full', 'Tier 2 Damage'
                            , 'Tier 2 Full'])
    # visible upon choosing broadband
    broadband = SelectField('Broadband Type:', choices=['Copper', 'Fibre 1', 'Fibre 2', 'Full Fibre'])
    submit = SubmitField('Submit')


# basic route for login page - linking to html file
@app.route('/')
def login():
    return render_template("login.html")


# route for users page
@app.route('/users/')
def users():
    return render_template("users.html")


# route for database page
@app.route('/database/')
def database():
    # connect to database and read all elements for products table
    conn = connect_db()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template("database.html", products=products)


# route for targets page
@app.route('/targets/')
def targets():
    return render_template("targets.html")


# route for sales tracker page
@app.route('/sales/', methods=['GET', 'POST'])
def sales():
    sales_form = SalesForm()
    # connect to database and read all elements for sales table
    conn = connect_db()
    all_sales = conn.execute('SELECT * FROM sales').fetchall()
    conn.close()
    return render_template("sales.html", sales_form=sales_form, all_sales=all_sales)


if __name__ == '__main__':
    app.run()

