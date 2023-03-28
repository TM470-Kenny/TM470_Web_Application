from flask import Flask, render_template

# instantiate the Flask object
app = Flask(__name__)


# basic route for login page - linking to html file
@app.route('/')
def login():
    return render_template("login.html")


# route for users page
@app.route('/users/')
def users():
    return render_template("users.html")


# route for database page
@app.route('/database/')
def database():
    return render_template("database.html")


# route for targets page
@app.route('/targets/')
def targets():
    return render_template("targets.html")


# route for sales tracker page
@app.route('/sales/')
def sales():
    return render_template("sales.html")


if __name__ == '__main__':
    app.run()
