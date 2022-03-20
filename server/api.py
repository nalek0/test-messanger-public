from flask import Blueprint

from user_api import user_api

api = Blueprint("api", __name__,
                url_prefix="/api")

api.register_blueprint(user_api)
