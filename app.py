import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app).cx["task_manager"]


@app.route("/")
@app.route("/get_books")

def get_books():
    books = mongo.books.find()
    return render_template("books.html", books=books)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already taken")
            return redirect(url_for("register"))
        
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.users.insert_one(register)

        # New user session
        session["user"] = request.form.get("username").lower()
        flash("Register was successful!")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Checks if username exists
        existing_user = mongo.users.find_one(
            {"username": request.form.get("username").lower()})
        # Checks if password matches
        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome {}".format(request.form.get("username")))
            else:
                flash("Incorrect User/Password")
                return redirect(url_for("login"))
            
        else:
            flash("Incorrect User/Password")
            return redirect(url_for("login"))


    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=True)