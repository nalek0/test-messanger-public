from flask import Blueprint, \
    request, redirect, url_for, render_template
from flask_login import login_user, logout_user

from database import db, User
from login_manager import login_manager

auth = Blueprint("auth", __name__,
                 url_prefix="/auth",
                 template_folder="templates/auth",
                 static_folder="static/auth")


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(user_id)


@auth.route("/signup", methods=["GET"])
def signup_get():
    return render_template("signup.html", error=request.args.get('error'))


@auth.route("/signup", methods=["POST"])
def signup_post():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    password = request.form.get('password')

    if User.query.filter_by(username=username).first() is not None:
        return redirect(url_for("auth.signup_get", error="username is already taken"))

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password=password
    )
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user, remember=True)

    next_url = request.form.get('next')

    return redirect(next_url or url_for("main.profile"))


@auth.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html", error=request.args.get('error'))


@auth.route("/login", methods=["POST"])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for("auth.login_get", error="No user with given username is found"))
    if user.password != password:
        return redirect(url_for("auth.login_get", error="Wrong password"))

    login_user(user, remember=True)

    next_url = request.form.get('next')

    return redirect(next_url or url_for("main.profile"))


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))
