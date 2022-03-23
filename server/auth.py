from flask import Blueprint, \
    request, redirect, url_for, render_template
from flask_login import login_user, logout_user, current_user
import hashlib

from database import db, User
from login_manager import login_manager
from templating import render_base_template

auth = Blueprint("auth", __name__,
                 url_prefix="/auth",
                 template_folder="templates/auth",
                 static_folder="static/auth")


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(user_id)


@auth.route("/signup", methods=["GET"])
def signup_get():
    return render_base_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    password = request.form.get('password')

    if User.query.filter_by(username=username).first() is not None:
        return redirect(url_for("auth.signup_get", errors=["Username is already taken"]))
    if not username.isalpha():
        return redirect(url_for("auth.signup_get", errors=["Username must contain only letters"]))

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password_hash=hashlib.sha256(password.encode('utf-8')).hexdigest()
    )
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user, remember=True)

    next_url = request.form.get('next')

    return redirect(next_url or url_for("main.profile", username=new_user.username))


@auth.route("/login", methods=["GET"])
def login_get():
    return render_base_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for("auth.login_get", errors=["No user with given username is found"]))
    if user.password_hash != hashlib.sha256(password.encode('utf-8')).hexdigest():
        return redirect(url_for("auth.login_get", errors=["Wrong password"]))

    login_user(user, remember=True)

    next_url = request.form.get('next')

    return redirect(next_url or url_for("main.profile", username=user.username))


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))
