import hashlib

from flask import Blueprint, request, redirect, url_for
from flask_login import login_user, logout_user

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


@auth.route("/signup")
def signup_page():
    return render_base_template("signup.html")


@auth.route("/login")
def login_page():
    return render_base_template("login.html")


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))
