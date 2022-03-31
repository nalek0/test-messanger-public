from pprint import pprint
from typing import List, Optional

from flask import Blueprint, request, abort
from flask_login import login_required, current_user
from werkzeug import exceptions

from database import User, db, Channel, Message, ChannelMember
from server.serializable import Serializable, serialize_list
from server_sockets import socketio

channel_api = Blueprint("channel_api", __name__,
                        url_prefix="/channel")


@channel_api.route("/get_channel", methods=["POST"])
@login_required
def get_channel():
    channel_id = request.json.get("channel_id")
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is None or \
            not current_channel.get_member(current_user).has_permission("watch_channel_information_permission"):
        return abort(exceptions.Forbidden.code)

    return current_channel.public_json()


@channel_api.route("/update_channel", methods=["POST"])
@login_required
def update_channel():
    channel_id = request.json.get("channel_id")
    channel = Channel.query.get(channel_id)
    if channel is None or \
            not channel.get_member(current_user).has_permission("edit_channel_permission"):
        return abort(exceptions.Forbidden.code)
    title = request.json.get("title") or ""
    description = request.json.get("description") or ""

    title.strip()
    description.strip()

    channel.title = title
    channel.description = description
    db.session.commit()

    channel.updated()

    return {"description": "OK"}


@channel_api.route("/get_member", methods=["POST"])
@login_required
def get_member():
    channel_id = request.json.get("channel_id")
    user_id = request.json.get("user_id")
    current_channel: Channel = Channel.query.get(channel_id)
    user: User = User.query.get(user_id)
    if current_channel is None or user is None or \
            not current_channel.get_member(current_user).has_permission("watch_channel_members_permission"):
        return abort(exceptions.Forbidden.code)
    else:
        member: Optional[ChannelMember] = current_channel.get_member(user)
        if member is None:
            return abort(exceptions.BadRequest.code)
        else:
            return member.public_json()


@channel_api.route("/fetch_members", methods=["POST"])
@login_required
def fetch_members():
    channel_id = request.json.get("channel_id")
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is None or \
            not current_channel.get_member(current_user).has_permission("watch_channel_members_permission"):
        return abort(exceptions.Forbidden.code)

    # Searching permissions:
    permissions = request.json.get("permissions")
    if permissions is not None:
        result = list(filter(
            lambda channel_member: all(map(lambda permission: channel_member.has_permission(permission), permissions)),
            current_channel.members
        ))[:20]
        print("result:", result)
        pprint(serialize_list(result))
        return {
            "data": serialize_list(result)
        }

    return abort(exceptions.BadRequest.code)


class MessagePage(Serializable):
    def __init__(self, page: int, messages: List[Message]):
        self.page = page
        self.messages = messages

    def public_json(self) -> dict:
        return {
            "page": self.page,
            "messages": serialize_list(self.messages),
        }


class MessageList(Serializable):
    def __init__(self, pages: List[MessagePage], channel: Channel) -> None:
        self.pages = pages
        self.channel = channel

    def public_json(self) -> dict:
        return {
            "pages": serialize_list(self.pages),
            "channel": self.channel.public_json(),
        }


@channel_api.route("/load_messages", methods=["POST"])
@login_required
def load_messages():
    number_of_messages_on_page = 20

    channel_id = request.json.get("channel_id")
    page = request.json.get("page")
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is None or \
            not current_channel.get_member(current_user).has_permission("read_channel_permission"):
        return abort(exceptions.Forbidden.code)

    def get_page_messages(p: int) -> List[Message]:
        q = current_channel.messages.query
        q.limit(number_of_messages_on_page)
        q.offset(p * number_of_messages_on_page)
        return q.all()

    def get_last_page_number() -> int:
        return current_channel.messages.count() // number_of_messages_on_page

    if page is None:
        # loading last 2 pages of messages
        last_page = get_last_page_number()
        if last_page == 0:
            return {
                "data": MessageList(
                    [MessagePage(0, current_channel.messages.all())],
                    current_channel
                ).public_json()
            }
        else:
            return {
                "data": MessageList(
                    [
                        MessagePage(last_page - 1, get_page_messages(last_page - 1)),
                        MessagePage(last_page, get_page_messages(last_page))
                    ],
                    current_channel
                ).public_json()
            }
    else:
        return {
            "data": MessageList(
                [MessagePage(page, get_page_messages(page))],
                current_channel
            ).public_json()
        }


@channel_api.route("/send_message", methods=["POST"])
@login_required
def send_message():
    channel_id = request.json.get("channel_id")
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is None or \
            not current_channel.get_member(current_user).has_permission("send_messages_permission"):
        return abort(exceptions.Forbidden.code)

    author: User = current_user
    text: str = request.json.get("text") or ""
    text = text.strip()
    if text == "":
        return abort(exceptions.BadRequest.code)

    new_message = Message(
        text=text,
        channel=current_channel,
        author=author
    )
    current_channel.messages.append(new_message)
    db.session.add(new_message)
    db.session.commit()

    socketio.emit("channel_message", new_message.public_json(), room=new_message.channel.room_id)

    return {
        "data": new_message.public_json()
    }
