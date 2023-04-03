from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField, IntegerField, DecimalField
from wtforms.validators import DataRequired, NumberRange


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


# form design for sales tracker form
class ProductsForm(FlaskForm):
    device_name = StringField('Device Name:')
    data_amount = IntegerField('Data Amount:')
    contract_length = SelectField('Contract Length:', choices=[12, 24, 36])
    price = DecimalField('Price:')
    revenue = DecimalField('Revenue:')
    commission = DecimalField('Commission:')
    submit = SubmitField('Submit')

