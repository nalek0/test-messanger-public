from flask_login import current_user
from flask_socketio import SocketIO

socketio = SocketIO()


@socketio.on('connect')
def socketio_event():
    if not current_user.is_anonymous:
        current_user.join_all_required_rooms()


@socketio.on('disconnect')
def socketio_event():
    if not current_user.is_anonymous:
        current_user.leave_all_required_rooms()
