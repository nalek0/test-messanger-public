from flask_login import current_user
from flask_socketio import SocketIO, join_room, leave_room

socketio = SocketIO()


@socketio.on('connect')
def socketio_event():
    if current_user is not None:
        current_user.join_all_required_rooms()


@socketio.on('disconnect')
def socketio_event():
    if current_user is not None:
        current_user.leave_all_required_rooms()
