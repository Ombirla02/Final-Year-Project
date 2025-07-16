from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.auth import auth
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User

from config.dbconnect import DatabaseConnection
db = DatabaseConnection().connection

users_collection = db["users"]

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user_data = users_collection.find_one({"email": email})
        print(user_data)
        if not user_data or not check_password_hash(user_data["password"], password):
            flash("Invalid credentials!", "error")
            return redirect(url_for("auth.login"))

        user = User.from_dict(user_data)
        login_user(user)

        print("Logged in user:", user)
        print("Session data:", session)
        if user.role == "supervisor":
            return redirect(url_for("supervisor.dashboard"))
        elif user.role == "industry_professional":
            return redirect(url_for("industry.dashboard"))
        else:
            return redirect(url_for("learner.dashboard"))

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("home.index"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]

    if users_collection.find_one({"email": email}):
        flash("Email already registered!", "danger")
        return redirect(url_for("auth.register"))

    hashed_password = generate_password_hash(password)
    new_user = User(username, email, hashed_password, role)
    users_collection.insert_one(new_user.to_dict())

    flash("Registration successful! You can now log in.", "success")
    return redirect(url_for("auth.login"))