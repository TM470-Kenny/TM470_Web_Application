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

# iphone = Products('iPhone 13', "", 20, 24, 59.99, 250, 2)
# samsung = Products('Samsung A53', "", 100, 24, 25.00, 200, 2)
# samsung1 = Products('Samsung S22', "", 999, 36, 65, 300, 2)
# iphone1 = Products('iPhone 13', "", 999, 24, 89, 310, 3)
# moto = Products('Moto G50', "", 2, 24, 18.00, 80, 2)
# bb = Products('', "Superfast 1", None, 24, 18.00, 80, 2)
# sim = Products('', "", 1, 24, 11.00, 80, 2)
# db.session.add_all([iphone, samsung, samsung1, iphone1, moto, bb, sim])
# #
# db.session.commit()


user1 = Users("guestadmin2", "Admin", "Guest", generate_password_hash("Password"), "admin2@mail.com", True, 2, 0)
user2 = Users("guestuser2", "User", "Guest", generate_password_hash("Password"), "user2@mail.com", False, 2, 0)
# user3 = Users("johnl", "John", "Love", generate_password_hash("Password"), "aa@gmail.com", True, 2, 0)
#
db.session.add_all([user2, user1])
#
db.session.commit()

# first_sale = Sales(user1.id, True, iphone.id, 10, "None", iphone.commission)
# second_sale = Sales(user2.id, True, moto.id, 0, "None", moto.commission)
# third_sale = Sales(user1.id, False, samsung.id, 20, "None", samsung.commission)
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
