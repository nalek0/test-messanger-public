from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint("main", __name__,
                 template_folder="templates/main",
                 static_folder="static/main")


@main.route("/")
def index():
    return "It's index!"


@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
