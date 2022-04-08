from configparser import ConfigParser

from flask import Flask

from api import api as api_blueprint
from database import db

CONFIG = ConfigParser()
CONFIG.read("image-processing.config")


def create_app():
    app = Flask(__name__)
    for key in CONFIG["Flask"].keys():
        app.config[key.upper()] = CONFIG["Flask"][key]

    db.init_app(app)

    app.register_blueprint(api_blueprint)

    return app


if __name__ == "__main__":
    create_app().run(host=CONFIG["RunConfig"]["host"],
                     port=CONFIG["RunConfig"].getint("port"),
                     debug=CONFIG["RunConfig"].getboolean("debug"))
