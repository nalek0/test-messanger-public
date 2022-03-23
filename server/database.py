import datetime as datetime
from typing import List

from flask import url_for
from flask_login import UserMixin
from flask_socketio import join_room, leave_room
from flask_sqlalchemy import SQLAlchemy

from serializable import Serializable, serialize_list
from server_sockets import socketio
import permissions

db = SQLAlchemy()

channel_membership_association_table = db.Table(
    'channel_membership_association_table',
    db.Column('user.id', db.Integer, db.ForeignKey('user.id')),
    db.Column('channel.id', db.Integer, db.ForeignKey('channel.id'))
)

user_friendship_association_table = db.Table(
    'user_friendship_association_table',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model, Serializable):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(400), default="")

    channels = db.relationship("Channel",
                               secondary=channel_membership_association_table,
                               backref="members")
    messages = db.relationship("Message", backref='author', lazy='dynamic')
    permissions = db.relationship("ChannelPermission", backref='user', lazy=True)

    friends = db.relationship('User',
                              secondary=user_friendship_association_table,
                              primaryjoin=(user_friendship_association_table.c.user_id == id),
                              secondaryjoin=(user_friendship_association_table.c.friend_id == id),
                              lazy='dynamic')

    def profile_url(self):
        return url_for("main.profile", username=self.username)

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "description": self.description
        }

    def private_json(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "description": self.description,
            "friends": serialize_list(self.friends)
        }

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def personal_private_room(self):
        return f"personal_user_private_room_{self.id}"

    def personal_public_room(self):
        return f"personal_user_public_room_{self.id}"

    def join_all_required_rooms(self):
        join_room(self.personal_private_room())
        for channel in self.channels:
            join_room(channel.room_id())

    def leave_all_required_rooms(self):
        leave_room(self.personal_private_room())
        for channel in self.channels:
            leave_room(channel.room_id())

    def updated(self):
        socketio.emit("user_private_data_changed", self.private_json(), room=self.personal_private_room())
        socketio.emit("user_public_data_changed", self.public_json(), room=self.personal_public_room())

    def __repr__(self):
        return '<User %r>' % self.username


class Channel(db.Model, Serializable):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), default="")
    description = db.Column(db.String(400), default="")
    # members: List[User]
    messages = db.relationship("Message", backref='channel', lazy=True)
    permissions = db.relationship("ChannelPermission", backref='channel', lazy=True)

    def room_id(self):
        return f"channel_room_{self.id}"

    def has_permissions_to_read(self, user: User) -> bool:
        return user in self.members

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "members": serialize_list(self.members),
            "permissions": serialize_list(self.permissions)
        }

    def get_user_permission(self, user: User):
        return UserPermission(user, self, list(filter(
            lambda permission: permission.user.id == user.id,
            self.permissions
        )))

    def personal_private_room(self):
        return f"personal_channel_private_room_{self.id}"

    def personal_public_room(self):
        return f"personal_channel_public_room_{self.id}"

    def updated(self):
        socketio.emit("channel_private_data_changed", self.private_json(), room=self.personal_private_room())
        socketio.emit("channel_public_data_changed", self.public_json(), room=self.personal_public_room())

    def __repr__(self):
        return f"<Channel {self.id}>"


class ChannelPermission(db.Model, Serializable):
    __tablename__ = 'channel_permission'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    permission_code = db.Column(db.Integer, nullable=False)

    def has_permission(self, permission: int) -> bool:
        return self.permission_code == permission

    def public_json(self) -> dict:
        return {
            "user": self.user.public_json(),
            "permission_code": self.permission_code
        }


class PermissionRole:
    def __init__(self, *channel_permissions: List[int]):
        self.channel_permissions = channel_permissions

    def set_permissions_for(self, channel: Channel, user: User):
        for permission_code in self.channel_permissions:
            channel.permissions.append(ChannelPermission(user_id=user.id, permission_code=permission_code))


AdminRole = PermissionRole(
    permissions.WATCH_CHANNEL_INFO,
    permissions.READ_CHANNEL,
    permissions.WATCH_CHANNEL_MEMBERS,
    permissions.SEND_MESSAGES,
    permissions.EDIT_CHANNEL,
    permissions.DELETE_CHANNEL)
ModeratorRole = PermissionRole(
    permissions.WATCH_CHANNEL_INFO,
    permissions.READ_CHANNEL,
    permissions.WATCH_CHANNEL_MEMBERS,
    permissions.SEND_MESSAGES,
    permissions.EDIT_CHANNEL)
MemberRole = PermissionRole(
    permissions.WATCH_CHANNEL_INFO,
    permissions.READ_CHANNEL,
    permissions.WATCH_CHANNEL_MEMBERS,
    permissions.SEND_MESSAGES)


class UserPermission:
    def __init__(self, user: User, channel: Channel, channel_permissions: List[ChannelPermission]):
        self.user = user
        self.channel = channel
        self.permissions = channel_permissions

    def has_permission(self, permission: int) -> bool:
        return any(map(
            lambda channel_permission: channel_permission.has_permission(permission),
            self.permissions
        ))


class Message(db.Model, Serializable):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "datetime": str(self.datetime),
            "channel": self.channel.public_json(),
            "author": self.author.public_json(),
        }

    def __repr__(self):
        return f"<Message {self.id}>"
