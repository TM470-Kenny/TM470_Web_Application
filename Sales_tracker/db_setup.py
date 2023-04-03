from main import db, Products, Users, Sales, app
app.app_context().push()
# creates all tables from models
db.create_all()

iphone = Products('iPhone 13', 20, 24, 59.99, 600, 3)
samsung = Products('Samsung A53', 100, 24, 25.00, 350, 2)

user1 = Users("kennyh", "Kenny", "Harvey", "Password")
user2 = Users("alonal", "Alona", "Lonsdale", "Password1")

db.session.add_all([iphone, samsung, user2, user1])

db.session.commit()

first_sale = Sales(user1.id, True, iphone.id, 10, False)
second_sale = Sales(user2.id, True, iphone.id, 0, True)
third_sale = Sales(user1.id, False, samsung.id, 20, True)

db.session.add_all([first_sale,second_sale,third_sale])

db.session.commit()

all_sales = Sales.query.all()
print(all_sales)

iphone.report_sales()