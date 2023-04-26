from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, IntegerField, DecimalField, PasswordField, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, NumberRange, InputRequired, Email

from models.products import Products
from models.users import Users


# form design for sales tracker form
class SalesForm(FlaskForm):
    # set as current logged in user - admin can change
    username = QuerySelectField('Username:', query_factory=lambda: Users.query, get_label="username", allow_blank=True, validators=[DataRequired()])
    new_up = BooleanField('New?')
    sale_type = SelectField('Sale Type:', choices=['Device', 'Sim', 'Broadband'])
    # visible upon choosing device
    device_name = QuerySelectField('Device Name:', query_factory=lambda: Products.query, get_label="device", allow_blank=True, validators=[DataRequired()])
    data_amount = QuerySelectField('Data Amount:', query_factory=lambda: Products.query, get_label="data", allow_blank=True, validators=[DataRequired()])
    contract_length = QuerySelectField('Contract Length:', query_factory=lambda: Products.query, get_label="length", allow_blank=True, validators=[DataRequired()])
    # price dependent on data and device selected
    price = QuerySelectField('Price:', query_factory=lambda: Products.query, get_label="price", allow_blank=True, validators=[DataRequired()])
    discount = IntegerField('Discount:', validators=[NumberRange(min=0, max=100)])
    # visible upon choosing device
    insurance = SelectField('Insurance:', choices=['None', 'Tier 1 Damage', 'Tier 1 Full', 'Tier 2 Damage'
                            , 'Tier 2 Full'])
    # visible upon choosing broadband
    broadband = SelectField('Broadband Type:', choices=['Copper', 'Fibre 1', 'Fibre 2', 'Full Fibre'])
    submit = SubmitField('Submit')


# form design for sales tracker form
class ProductsForm(FlaskForm):
    device_name = StringField('Device Name:')
    data_amount = IntegerField('Data Amount:')
    contract_length = SelectField('Contract Length:', choices=['', 12, 24, 36])
    price = DecimalField('Price:')
    revenue = DecimalField('Revenue:')
    commission = DecimalField('Commission:')
    submit = SubmitField('Submit')


class UsersForm(FlaskForm):
    firstname = StringField('First name:', validators=[InputRequired()])
    lastname = StringField('Last name:', validators=[InputRequired()])
    email = StringField('Email:', validators=[Email()])
    admin = BooleanField('Admin?')
    store_id = SelectField('Store ID:', choices=['', 1])
    submit = SubmitField('Submit')


class TargetForm(FlaskForm):
    new = IntegerField('New:')
    upgrades = IntegerField('Upgrades:')
    broadband = IntegerField('Broadband:')
    unlimited = IntegerField('Unlimited:')
    insurance = IntegerField('Insurance:')
    revenue = IntegerField('Revenue:')
    submit = SubmitField('Submit')


class HoursForm(FlaskForm):
    username = StringField('Username:')
    hours = IntegerField('Hours working:')
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField('Log In')



