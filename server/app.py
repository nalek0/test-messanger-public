from configparser import ConfigParser
from flask import Flask

from database import db
from login_manager import login_manager

from auth import auth as auth_blueprint
from main import main as main_blueprint
from messanger import messanger as messanger_blueprint

config = ConfigParser()
config.read("flask.config")

app = Flask(__name__)
for key in config["Flask"].keys():
    app.config[key.upper()] = config["Flask"][key]

db.init_app(app)
login_manager.init_app(app)


app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(messanger_blueprint)

if __name__ == "__main__":
    app.run(host=config["RunConfig"]["host"],
            port=config["RunConfig"].getint("port"),
            debug=config["RunConfig"].getboolean("debug"))
