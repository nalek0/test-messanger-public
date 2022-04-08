from flask import Blueprint, jsonify
from werkzeug.exceptions import BadRequestKeyError, Unauthorized
from api_exceptions import *
from api_image import image_api


api = Blueprint("api", __name__,
                url_prefix="/api")


@api.errorhandler(Unauthorized.code)
def unauthorized_errorhandler(_):
    error = APIUnauthorized()
    return jsonify(error.dict), error.status_code


@api.errorhandler(BadRequestKeyError)
def invalid_api_usage(exception: BadRequestKeyError):
    api_exception = APIBadRequest.make_from(exception)
    return jsonify(api_exception.dict), api_exception.status_code


@api.errorhandler(APIException)
def invalid_api_usage(exception: APIException):
    return jsonify(exception.dict), exception.status_code


api.register_blueprint(image_api)
