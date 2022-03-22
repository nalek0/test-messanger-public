from typing import List

from flask import Blueprint, request, abort
from flask_login import login_required, current_user
from werkzeug import exceptions

from database import User, db, Channel, Message
from server.serializable import Serializable, serialize_list
from server_sockets import socketio

channel_api = Blueprint("channel_api", __name__,
                        url_prefix="/channel")


class MessageList(Serializable):
    def __init__(self, messages: List[Message], channel: Channel) -> None:
        self.messages = messages
        self.channel = channel

    def json(self) -> dict:
        return {
            "messages": serialize_list(self.messages),
            "channel": self.channel.json(),
        }


@channel_api.route("/load_messages", methods=["POST"])
@login_required
def load_messages():
    channel_id = request.json.get("channel_id")
    current_channel: Channel = Channel.query.get_or_404(channel_id)
    if not current_channel.has_permissions_to_read(current_user):
        return abort(exceptions.Forbidden.code)

    return {
        "data": MessageList(current_channel.messages, current_channel).json()
    }


@channel_api.route("/send_message", methods=["POST"])
@login_required
def send_message():
    channel_id = request.json.get("channel_id")
    current_channel: Channel = Channel.query.get_or_404(channel_id)
    if not current_channel.has_permissions_to_read(current_user):
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

    socketio.emit("channel_message", new_message.json(), room=new_message.channel.room_id())

    return {
        "data": new_message.json()
    }
