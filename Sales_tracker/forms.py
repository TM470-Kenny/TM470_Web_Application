from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, IntegerField, DecimalField, PasswordField, ValidationError, HiddenField
from wtforms.validators import DataRequired, InputRequired, Email, Optional


def multi_validate(form, field):
    if form.sale_type.data == "Broadband":
        if not form.broadband.data:
            raise ValidationError("Broadband field required")
    if form.sale_type.data == "Sim Only":
        if not form.data_amount.data:
            raise ValidationError("Data field required")
    if form.sale_type.data == "Device":
        if not form.data_amount.data or not form.device_name.data:
            raise ValidationError(field.gettext("error"))


# form design for sales tracker form
class SalesForm(FlaskForm):
    # set as current logged in user - admin can change
    sale_id = HiddenField(id="sale_id")
    username = SelectField('Username:', validators=[DataRequired()], id='select_user')
    sale_type = SelectField('Sale Type:', validators=[DataRequired()], choices=["", 'Device', 'Sim Only', 'Broadband'], id="types")
    # visible upon choosing device
    new_up = BooleanField('New?', id="new_choice")
    device_name = SelectField('Device Name:', id='select_device', validators=[multi_validate])
    data_amount = SelectField('Data Amount:', id='select_data', validators=[Optional(), multi_validate])
    broadband = SelectField('Broadband Type:', id="bb", validators=[multi_validate])
    contract_length = SelectField('Contract Length:', validators=[DataRequired()], id='select_length')
    # price dependent on data and device selected
    price = SelectField('Price:', validators=[DataRequired()], id='select_price')
    discount = SelectField('Discount:', validators=[DataRequired()], choices=[0, 5, 10, 15, 20], id="disc")
    # visible upon choosing device
    insurance = SelectField('Insurance:', validators=[DataRequired()], choices=['None', 'Tier 1 Damage', 'Tier 1 Full', 'Tier 2 Damage'
                            , 'Tier 2 Full'], id="ins")
    # visible upon choosing broadband
    submit = SubmitField('Submit')



# form design for sales tracker form
class ProductsForm(FlaskForm):
    product_id = HiddenField(id='product_id')
    product_type = SelectField('Product type:', choices=['', 'Device', 'Sim Only', 'Broadband'], validators=[DataRequired()], id='product')
    device_name = StringField('Device Name:', id='device')
    broadband_name = StringField('Broadband plan:', id='bb')
    data_amount = IntegerField('Data Amount:', id='amount', validators=[Optional()])
    contract_length = SelectField('Contract Length:', choices=['', 12, 24, 36], validators=[DataRequired()], id='contract')
    price = DecimalField('Price:', validators=[DataRequired()], id='price')
    revenue = DecimalField('Revenue:', validators=[DataRequired()], id='rev')
    commission = DecimalField('Commission:', validators=[DataRequired()], id='comm')
    submit = SubmitField('Submit')


class UsersForm(FlaskForm):
    user_id = HiddenField(id='user_id')
    firstname = StringField('First name:', validators=[InputRequired()])
    lastname = StringField('Last name:', validators=[InputRequired()])
    email = StringField('Email:', validators=[Email()])
    admin = BooleanField('Admin?')
    store_id = SelectField('Store ID:', choices=['', 1, 2])
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



