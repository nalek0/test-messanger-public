from flask import Blueprint, request, escape
from flask_login import login_required, current_user

from database import User
from templating import render_base_template

main = Blueprint("main", __name__,
                 template_folder="templates/main",
                 static_folder="static/main")


@main.route("/")
def index():
    return render_base_template("index.html")


@main.route("/profile/<username>")
@login_required
def profile(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    return render_base_template("profile.html", user=user)


@main.route("/profile")
@login_required
def client_profile():
    return render_base_template("personal-profile.html")


@main.route("/friends")
@login_required
def friends():
    return render_base_template("friends.html")


@main.route("/search")
def search_page():
    recommendations = User.query.limit(10).all()
    return render_base_template("search_page.html", recommendations=recommendations)


@main.route("/channels")
@main.route("/channels/<int:page>")
@login_required
def channels(page: int = 0):
    return render_base_template("channels.html", page=page, number_of_pages=1)


@main.route("/create_channel")
@login_required
def create_channel():
    return render_base_template("create_channel.html")


@main.route("/search", methods=["POST"])
def search_result():
    query = escape(request.form["query"])
    like_query = "%{}%".format(query)
    users = User.query\
        .filter(User.username.like(like_query))\
        .limit(10).all()
    return render_base_template("search_results_page.html", results=users, query=query)
