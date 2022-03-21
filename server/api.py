from flask import Blueprint

from api_channel import channel_api
from api_user import user_api

api = Blueprint("api", __name__,
                url_prefix="/api")

api.register_blueprint(user_api)
api.register_blueprint(channel_api)
