from main import db, Products, Users, Sales, app, StoreTargets, Targets
app.app_context().push()
# creates all tables from models
db.create_all()

iphone = Products('iPhone 13', 20, 24, 59.99, 600, 3)
samsung = Products('Samsung A53', 100, 24, 25.00, 350, 2)

user1 = Users("kennyh", "Kenny", "Harvey", "Password", True, 1)
user2 = Users("alonal", "Alona", "Lonsdale", "Password1", False, 1)

db.session.add_all([iphone, samsung, user2, user1])

db.session.commit()

first_sale = Sales(user1.id, True, iphone.id, 10, False)
second_sale = Sales(user2.id, True, iphone.id, 0, True)
third_sale = Sales(user1.id, False, samsung.id, 20, True)

db.session.add_all([first_sale,second_sale,third_sale])

db.session.commit()

store_target = StoreTargets(50, 80, 9, 25, 12, 5850)
db.session.add(store_target)
db.session.commit()

user1_target = Targets(store_target.id, user1.username, 10, 15, 2, 5, 2, 1000)
db.session.add(user1_target)
db.session.commit()
