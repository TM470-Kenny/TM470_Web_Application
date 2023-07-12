from db import db
from models.products import Products
from models.users import Users


class Sales(db.Model):

    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    new = db.Column(db.Boolean, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    discount = db.Column(db.Integer)
    insurance = db.Column(db.Text, nullable=True)
    commission = db.Column(db.Numeric, nullable=False)

    def __init__(self, user, new, product_id, discount, insurance, commission):
        self.user = user
        self.new = new
        self.product_id = product_id
        self.discount = discount
        self.insurance = insurance
        self.commission = commission

    def __repr__(self):
        return f'Sale by {Users.query.filter_by(id=self.user).first().username} of product with id {Products.query.filter_by(id=self.product_id).first().id} with {self.discount}% discount and {self.insurance} insurance'
