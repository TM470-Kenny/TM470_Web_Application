from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, IntegerField, DecimalField, PasswordField, ValidationError, HiddenField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, NumberRange, InputRequired, Email

from models.products import Products
from models.users import Users


# form design for sales tracker form
class SalesForm(FlaskForm):
    # set as current logged in user - admin can change
    sale_id = HiddenField(id="sale_id")
    username = SelectField('Username:', validators=[DataRequired()], id='select_user')
    new_up = BooleanField('New?')
    sale_type = SelectField('Sale Type:', choices=['Device', 'Sim', 'Broadband'])
    # visible upon choosing device
    device_name = SelectField('Device Name:', validators=[DataRequired()], id='select_device')
    data_amount = SelectField('Data Amount:', validators=[DataRequired()], id='select_data')
    contract_length = SelectField('Contract Length:', validators=[DataRequired()], id='select_length')
    # price dependent on data and device selected
    price = SelectField('Price:', validators=[DataRequired()], id='select_price')
    discount = IntegerField('Discount:', validators=[NumberRange(min=0, max=100)])
    # visible upon choosing device
    insurance = SelectField('Insurance:', choices=['None', 'Tier 1 Damage', 'Tier 1 Full', 'Tier 2 Damage'
                            , 'Tier 2 Full'])
    # visible upon choosing broadband
    broadband = SelectField('Broadband Type:', choices=['Copper', 'Fibre 1', 'Fibre 2', 'Full Fibre'])
    submit = SubmitField('Submit')


# form design for sales tracker form
class ProductsForm(FlaskForm):
    product_id = HiddenField(id='product_id')
    device_name = StringField('Device Name:', validators=[DataRequired()])
    data_amount = IntegerField('Data Amount:', validators=[DataRequired()])
    contract_length = SelectField('Contract Length:', choices=['', 12, 24, 36], validators=[DataRequired()])
    price = DecimalField('Price:', validators=[DataRequired()])
    revenue = DecimalField('Revenue:', validators=[DataRequired()])
    commission = DecimalField('Commission:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UsersForm(FlaskForm):
    user_id = HiddenField(id='user_id')
    firstname = StringField('First name:', validators=[InputRequired()])
    lastname = StringField('Last name:', validators=[InputRequired()])
    email = StringField('Email:', validators=[Email()])
    admin = BooleanField('Admin?')
    store_id = SelectField('Store ID:', choices=['', 1])
    submit = SubmitField('Submit')


class TargetForm(FlaskForm):
    new = IntegerField('New:', validators=[DataRequired()])
    upgrades = IntegerField('Upgrades:', validators=[DataRequired()])
    broadband = IntegerField('Broadband:', validators=[DataRequired()])
    unlimited = IntegerField('Unlimited:', validators=[DataRequired()])
    insurance = IntegerField('Insurance:', validators=[DataRequired()])
    revenue = IntegerField('Revenue:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class HoursForm(FlaskForm):
    username = SelectField('Username:', validators=[DataRequired()])
    hours = IntegerField('Hours working:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField('Log In')



