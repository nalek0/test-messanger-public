from flask import Blueprint, request, abort
from flask_login import login_required, current_user

from database import User, db

user_api = Blueprint("user_api", __name__,
                     url_prefix="/user")


@user_api.route("/add-friend", methods=["POST"])
@login_required
def add_friend():
    user_id = request.json.get("user_id") or abort(400)
    user = User.query.get_or_404(user_id)
    if user not in current_user.friends:
        current_user.friends.append(user)
        db.session.commit()
        return {
            "description": "OK"
        }
    else:
        return {
            "description": "This user is already friend"
        }


@user_api.route("/remove-friend", methods=["POST"])
@login_required
def remove_friend():
    user_id = request.form["user_id"] or abort(400)
    user = User.query.get_or_404(user_id)
    if user in current_user.friends:
        current_user.friends.remove(user)
        db.session.commit()
        return {
            "description": "OK"
        }
    else:
        return {
            "description": "This user is already not friend"
        }
