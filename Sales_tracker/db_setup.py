from werkzeug.security import generate_password_hash

from main import app
from db import db
from models.products import Products
from models.targets import StoreTargets, Targets, Progress
from models.users import Users
from models.sales import Sales

app.app_context().push()
db.init_app(app)
# creates all tables from models
db.create_all()

# iphone = Products('iPhone 13', 20, 24, 59.99, 600, 3)
# samsung = Products('Samsung A53', 100, 24, 25.00, 350, 2)
#
user1 = Users("kennyh", "Kenny", "Harvey", generate_password_hash("Password"), "kenny@gmail.com", True, 1, 0)
user2 = Users("alonal", "Alona", "Lonsdale", generate_password_hash("Password1"), "alona@gmail.com", False, 1, 0)
user3 = Users("johnl", "John", "Love", generate_password_hash("Password"), "aa@gmail.com", True, 2, 0)
#
db.session.add_all([user2, user1, user3])
#
db.session.commit()

# first_sale = Sales(user1.id, True, iphone.id, 10, False)
# second_sale = Sales(user2.id, True, iphone.id, 0, True)
# third_sale = Sales(user1.id, False, samsung.id, 20, True)
#
# db.session.add_all([first_sale,second_sale,third_sale])
#
# db.session.commit()

# store_target = StoreTargets(50, 80, 9, 25, 12, 5850)
# db.session.add(store_target)
# db.session.commit()

# user_progress = Progress(user1.id, 3, 6, 1, 2, 0, 800)
# db.session.add(user_progress)
# db.session.commit()

# user1_target = Targets(store_target.id, user1.id, 10, 15, 2, 5, 2, 1000)
# db.session.add(user1_target)
# db.session.commit()
