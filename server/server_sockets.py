from flask_login import current_user
from flask_socketio import SocketIO, join_room, leave_room

socketio = SocketIO()


@socketio.on('connect')
def socketio_event():
    if current_user is not None:
        for channel in current_user.channels:
            join_room(channel.room_id())


@socketio.on('disconnect')
def socketio_event():
    if current_user is not None:
        for channel in current_user.channels:
            leave_room(channel.room_id())
