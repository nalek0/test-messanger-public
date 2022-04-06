from flask import Blueprint, request
from flask_login import login_required, current_user

from api_exceptions import APINotFound
from database import ChannelInvitation

invitation_api = Blueprint("invitation_api", __name__,
                           url_prefix="/invitation")


@invitation_api.route("/delete", methods=["POST"])
@login_required
def delete_invitation():
    invitation_id = request.json["invitation_id"]
    invitation = ChannelInvitation.query.get(invitation_id)
    if invitation is None or invitation.user.id != current_user.id:
        raise APINotFound(f"You have no invitations with {invitation_id} id")

    invitation.delete()

    return {"description": "OK"}


@invitation_api.route("/use", methods=["POST"])
@login_required
def use_invitation():
    invitation_id = request.json["invitation_id"]
    invitation = ChannelInvitation.query.get(invitation_id)
    if invitation is None or invitation.user.id != current_user.id:
        raise APINotFound(f"You have no invitations with {invitation_id} id")

    invitation.use()

    return {"description": "OK"}