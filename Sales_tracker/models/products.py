from db import db


class Products(db.Model):

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.Text)
    data = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    revenue = db.Column(db.Numeric, nullable=False)
    commission = db.Column(db.Numeric, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    # Set up One to Many relationship
    product_sales = db.relationship('Sales', backref='product', lazy='dynamic')

    def __init__(self, device, data, length, price, revenue, commission):
        self.device = device
        self.data = data
        self.length = length
        self.price = price
        self.revenue = revenue
        self.commission = commission
        self.is_deleted = False

    def __repr__(self):
        return f'{self.device} with {self.data}GB at £{round(self.price, 2)} for {self.length} months'

    @classmethod
    def all_length(cls, device, data):
        return Products.query.filter_by(device=device, data=data).all()
