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
    books = list(mongo.books.find())
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

@app.route("/logout")
# User Log Out
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))

@app.route("/addbook", methods=["GET", "POST"])
def addbook():
    if request.method == "POST":
        book = {
            "book_name": request.form.get("book_name"),
            "release_year": request.form.get("release_year"),
            "author": request.form.get("author"),
            "summary": request.form.get("summary"),
            "created_by": session["user"]
        }
        mongo.books.insert_one(book)
        flash("Book added succesfully!")
        return redirect(url_for("get_books"))
    
    return render_template("addbook.html")

@app.route("/editbook/<book_id>", methods=["GET", "POST"])
def editbook(book_id):
    if request.method == "POST":
        booksubmit = {
            "book_name": request.form.get("book_name"),
            "release_year": request.form.get("release_year"),
            "author": request.form.get("author"),
            "summary": request.form.get("summary"),
            "created_by": session["user"]
        }
        mongo.books.replace_one({"_id": ObjectId(book_id)}, booksubmit)
        flash("Book updated succesfully!")

    book = mongo.books.find_one({"_id": ObjectId(book_id)})
    return render_template("editbook.html", book=book)

@app.route("/deletebook/<book_id>")
def deletebook(book_id):
    mongo.books.delete_one({"_id": ObjectId(book_id)})
    flash("Book successfully deleted")
    return redirect(url_for("get_books"))



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=True)