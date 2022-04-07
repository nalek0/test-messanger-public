from typing import List, Optional

from flask import Blueprint, request, abort
from flask_login import login_required, current_user
from werkzeug import exceptions

from api_exceptions import *
from database import User, db, Channel, Message, ChannelMember, ChannelInvitation, ChannelFabric
from server.serializable import Serializable, serialize_list
from server_sockets import socketio

channel_api = Blueprint("channel_api", __name__,
                        url_prefix="/channel")


class APIDoNotHavePermission(APIForbidden):
    def __init__(self, permission: str) -> None:
        super().__init__(f"You do not have '{permission}' permission")


@channel_api.route("/get", methods=["POST"])
@login_required
def get_channel():
    channel_id = request.json["channel_id"]
    current_channel = Channel.query.get(channel_id)
    if current_channel is None:
        raise APINotFound(f"Channel with {channel_id} id is not found")

    if current_channel.get_member(current_user).has_permission("watch_channel_information_permission"):
        return current_channel.public_json()
    else:
        raise APIDoNotHavePermission("watch_channel_information_permission")


@channel_api.route("/update", methods=["POST"])
@login_required
def update_channel():
    channel_id = request.json["channel_id"]
    channel = Channel.query.get(channel_id)
    if channel is None:
        raise APINotFound(f"Channel with {channel_id} id is not found")
    if not channel.get_member(current_user).has_permission("edit_channel_permission"):
        raise APIDoNotHavePermission("edit_channel_permission")

    title = request.json.get("title")
    if title is not None:
        channel.title = title.strip()
    description = request.json.get("title")
    if description is not None:
        channel.description = description.strip()

    db.session.commit()
    channel.updated()

    return {"description": "OK"}


@channel_api.route("/create", methods=["POST"])
@login_required
def create_channel():
    title = request.json["title"]
    description = request.json.get("description", "")
    companions = request.json.get("companions", [])

    other_users = list(map(
        lambda companion_id: User.query.get(companion_id),
        companions
    ))
    if any(map(lambda el: el is None, other_users)):
        raise APIBadRequest("Not all companions exists")

    return ChannelFabric(title, description, other_users, current_user).make().public_json()


@channel_api.route("/member/get", methods=["POST"])
@login_required
def get_member():
    channel_id = request.json["channel_id"]
    user_id = request.json["user_id"]

    current_channel = Channel.query.get(channel_id)
    if current_channel is None:
        raise APINotFound(f"Channel with {channel_id} id is not found")

    user = User.query.get(user_id)
    if user is None:
        raise APINotFound(f"User with {user_id} id is not found")

    if not current_channel.get_member(current_user).has_permission("watch_channel_members_permission"):
        raise APIDoNotHavePermission("watch_channel_members_permission")
    else:
        member: Optional[ChannelMember] = current_channel.get_member(user)
        if member is None:
            raise APIBadRequest(f"User with {user_id} id is not member of the channel with {channel_id} id")
        else:
            return member.public_json()


@channel_api.route("/member/fetch", methods=["POST"])
@login_required
def fetch_members():
    channel_id = request.json["channel_id"]
    current_channel = Channel.query.get(channel_id)
    if current_channel is None:
        raise APINotFound(f"Channel with {channel_id} id is not found")
    if not current_channel.get_member(current_user).has_permission("watch_channel_members_permission"):
        raise APIDoNotHavePermission("watch_channel_members_permission")

    # Fetch criteria:
    results = current_channel.members

    # Searching permissions:
    permissions = request.json.get("permissions")
    if permissions is not None:
        if permissions is not List[str]:
            raise APIBadRequest("permissions must be List[str]")

        results = list(filter(
            lambda channel_member: all(map(lambda permission: channel_member.has_permission(permission), permissions)),
            results
        ))

    page = request.json.get("page") or 0
    page_results = request.json.get("page_results") or 20
    if page is not int or page < 0:
        raise APIBadRequest("Wrong page parameter")
    if page_results is not int or page_results <= 0 or page_results > 50:
        raise APIBadRequest("Wrong page_results parameter")

    results_on_page = results[page * page_results:
                              (page + 1) * page_results]

    return {"data": serialize_list(results_on_page)}


@channel_api.route("/message/fetch", methods=["POST"])
@login_required
def fetch_messages():
    channel_id = request.json["channel_id"]
    current_channel = Channel.query.get(channel_id)
    if current_channel is None:
        raise APINotFound(f"Channel with {channel_id} id is not found")
    if not current_channel.get_member(current_user).has_permission("read_channel_permission"):
        raise APIDoNotHavePermission("read_channel_permission")

    page = request.json.get("page") or 0
    page_results = request.json.get("page_results") or 20
    if page is not int or page < 0:
        raise APIBadRequest("Wrong page parameter")
    if page_results is not int or page_results <= 0 or page_results > 50:
        raise APIBadRequest("Wrong page_results parameter")

    messages_query = current_channel.messages.query
    messages_query.limit(page_results)
    messages_query.offset(page * page_results)

    return {"data": serialize_list(messages_query.all())}


@channel_api.route("/message/send", methods=["POST"])
@login_required
def send_message():
    channel_id = request.json["channel_id"]
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is None:
        raise APINotFound(f"Channel with {channel_id} id is not found")
    if not current_channel.get_member(current_user).has_permission("send_messages_permission"):
        raise APIDoNotHavePermission("send_messages_permission")

    author: User = current_user
    text: str = request.json["text"].strip()
    if text == "":
        raise APIBadRequest("Text must not be blank")

    new_message = Message(
        text=text,
        channel=current_channel,
        author=author
    )
    current_channel.messages.append(new_message)
    db.session.add(new_message)
    db.session.commit()

    socketio.emit("channel_message", new_message.public_json(), room=new_message.channel.room_id)

    return {"data": new_message.public_json()}
