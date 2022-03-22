from configparser import ConfigParser

from flask import Flask

from api import api as api_blueprint
from auth import auth as auth_blueprint
from database import db
from login_manager import login_manager
from main import main as main_blueprint
from messanger import messanger as messanger_blueprint
from server_sockets import socketio

CONFIG = ConfigParser()
CONFIG.read("flask.config")


def create_app():
    app = Flask(__name__)
    for key in CONFIG["Flask"].keys():
        app.config[key.upper()] = CONFIG["Flask"][key]

    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(messanger_blueprint)
    app.register_blueprint(api_blueprint)

    return app


if __name__ == "__main__":
    socketio.run(create_app(),
                 host=CONFIG["RunConfig"]["host"],
                 port=CONFIG["RunConfig"].getint("port"),
                 debug=CONFIG["RunConfig"].getboolean("debug"))
