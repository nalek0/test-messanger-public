from flask import Blueprint, render_template, redirect, url_for, request, escape
from flask_login import login_required, current_user

from database import User

main = Blueprint("main", __name__,
                 template_folder="templates/main",
                 static_folder="static/main")


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/profile/<username>")
@login_required
def profile(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("profile.html", user=user)


@main.route("/profile")
@login_required
def client_profile():
    return render_template("profile.html", user=current_user)


@main.route("/search")
def search_page():
    recommendations = User.query.limit(10).all()
    return render_template("search_page.html", recommendations=recommendations)


@main.route("/search", methods=["POST"])
def search_result():
    query = escape(request.form["query"])
    like_query = "%{}%".format(query)
    users = User.query\
        .filter(User.username.like(like_query))\
        .limit(10).all()
    return render_template("search_results_page.html", results=users, query=query)
