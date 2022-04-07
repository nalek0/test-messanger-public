from flask import Blueprint, render_template

pages = Blueprint("pages", __name__,
                  static_folder="static/main",
                  url_prefix="/")


@pages.route("/")
def index():
    return render_template("index.html")
