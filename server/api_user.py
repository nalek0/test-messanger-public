import hashlib
import json

import requests as requests
from flask import Blueprint, request
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.exceptions import abort

from api_exceptions import APINotFound, APIBadRequest, APIForbidden
from database import User, db
from apis_urls import APIS_CONFIG

user_api = Blueprint("user_api", __name__,
                     url_prefix="/user")


@user_api.route("/get", methods=["POST"])
def get_user():
    print(request.data)
    dt = json.loads(request.data)
    print(dt)
    user_id = dt["user_id"]
    user = User.query.get(user_id)
    if user is not None:
        return user.public_json()
    else:
        raise APINotFound(f"User with given ({user_id}) is not found!")


@user_api.route("/client/signup", methods=["POST"])
def client_signup():
    first_name = request.json["first_name"].strip()
    last_name = request.json["last_name"].strip()
    username = request.json["username"].lower().strip()
    password = request.json["password"]

    if User.query.filter_by(username=username).first() is not None:
        raise APIForbidden(f"Username {username} is already taken")
    if not username.isalpha():
        raise APIForbidden(f"Username must contain only letters")
    if first_name == "" or last_name == "":
        raise APIBadRequest("First and last names must be not blank")

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password_hash=hashlib.sha256(password.encode('utf-8')).hexdigest()
    )
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user, remember=True)

    return current_user.private_json()


@user_api.route("/client/login", methods=["POST"])
def login_post():
    username = request.json["username"].lower()
    password = request.json["password"]

    user = User.query.filter_by(username=username).first()
    if user is None:
        raise APINotFound("No user with given username is found")
    if user.password_hash != hashlib.sha256(password.encode('utf-8')).hexdigest():
        raise APIForbidden("Wrong password")

    login_user(user, remember=True)

    return current_user.private_json()


@user_api.route("/client/logout")
@login_required
def logout():
    logout_user()
    return {"description": "OK"}


@user_api.route("/client/get", methods=["POST"])
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
    if request.json.get("avatar") is not None:
        image_base64 = request.json.get("avatar")
        response = requests.post(url=f"{APIS_CONFIG['OtherAPI']['ImageProcessing']}/api/image/add",
                                 json={"image": image_base64},
                                 timeout=2)
        if response.status_code not in range(200, 300):
            return abort(response.status_code)
        current_user.set_avatar(response.json())

    db.session.commit()
    current_user.updated()

    return current_user.private_json()


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
