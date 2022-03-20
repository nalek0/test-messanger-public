from flask import Blueprint

from api_user import user_api

api = Blueprint("api", __name__,
                url_prefix="/api")

api.register_blueprint(user_api)
