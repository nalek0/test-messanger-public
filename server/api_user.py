from flask import Blueprint, request
from flask_login import login_required, current_user

from api_exceptions import APINotFound, APIBadRequest
from database import User, db

user_api = Blueprint("user_api", __name__,
                     url_prefix="/user")


@user_api.route("/get", methods=["GET"])
def get_user():
    user_id = request.args["user_id"]
    user = User.query.get(user_id)
    if user is not None:
        return user.public_json()
    else:
        raise APINotFound(f"User with given ({user_id}) is not found!")


@user_api.route("/client/get", methods=["GET"])
@login_required
def get_client():
    return current_user.private_json()


@user_api.route("/client/update", methods=["POST"])
@login_required
def update_profile():
    if request.json.get("first_name") is not None:
        first_name = request.json.get("first_name").strip()
        if first_name == "":
            raise APIBadRequest("First name must not be blank")
        current_user.first_name = first_name
    if request.json.get("last_name") is not None:
        last_name = request.json.get("last_name").strip()
        if last_name == "":
            raise APIBadRequest("Last name must not be blank")
        current_user.last_name = last_name
    if request.json.get("description") is not None:
        description = request.json.get("description").strip()
        current_user.description = description

    db.session.commit()
    current_user.updated()

    return {"description": "OK"}


@user_api.route("/client/friend/add", methods=["POST"])
@login_required
def add_friend():
    user_id = request.json["user_id"]
    user = User.query.get(user_id)
    if user is None:
        raise APINotFound(f"User with given ({user_id}) is not found!")

    if user not in current_user.friends:
        current_user.friends.append(user)
        db.session.commit()
        current_user.updated()

        return {"description": "OK"}
    else:
        return {"description": "This user is already friend"}


@user_api.route("/client/friend/remove", methods=["POST"])
@login_required
def remove_friend():
    user_id = request.json["user_id"]
    user = User.query.get(user_id)
    if user is None:
        raise APINotFound(f"User with given ({user_id}) is not found!")

    if user in current_user.friends:
        current_user.friends.remove(user)
        db.session.commit()
        current_user.updated()

        return {"description": "OK"}
    else:
        return {"description": "This user is already not friend"}
