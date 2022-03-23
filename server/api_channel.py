from typing import List

from flask import Blueprint, request, abort
from flask_login import login_required, current_user
from werkzeug import exceptions

from database import User, db, Channel, Message
from server import permissions
from server.serializable import Serializable, serialize_list
from server_sockets import socketio

channel_api = Blueprint("channel_api", __name__,
                        url_prefix="/channel")


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
            not current_channel\
            .get_user_permission(current_user)\
            .has_permission(permission=permissions.READ_CHANNEL):
        return abort(exceptions.Forbidden.code)

    def get_page_messages(p: int) -> List[Message]:
        return current_channel.messages[p * number_of_messages_on_page:(p + 1) * number_of_messages_on_page]

    def get_last_page_number() -> int:
        return len(current_channel.messages) // number_of_messages_on_page

    if page is None:
        # loading last 2 pages of messages
        last_page = get_last_page_number()
        if last_page == 0:
            return {
                "data": MessageList(
                    [MessagePage(0, current_channel.messages)],
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
            not current_channel\
            .get_user_permission(current_user)\
            .has_permission(permission=permissions.SEND_MESSAGES):
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

    socketio.emit("channel_message", new_message.public_json(), room=new_message.channel.room_id())

    return {
        "data": new_message.public_json()
    }
