from db import db


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
