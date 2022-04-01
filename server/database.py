import datetime as datetime
from typing import List

from flask import url_for
from flask_login import UserMixin
from flask_socketio import join_room, leave_room
from flask_sqlalchemy import SQLAlchemy

from serializable import Serializable, serialize_list
from server_sockets import socketio

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
                               backref="users",
                               lazy=True)
    membership = db.relationship("ChannelMember",
                                 backref='user',
                                 lazy=True)
    messages = db.relationship("Message",
                               backref='author',
                               lazy='dynamic')
    friends = db.relationship('User',
                              secondary=user_friendship_association_table,
                              primaryjoin=(user_friendship_association_table.c.user_id == id),
                              secondaryjoin=(user_friendship_association_table.c.friend_id == id),
                              lazy=True)
    user_roles = db.relationship('UserRole',
                                 backref='user',
                                 lazy=True)

    @property
    def profile_url(self):
        return url_for("main.profile", username=self.username)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def personal_public_room(self):
        return f"personal_user_public_room_{self.id}"

    @property
    def personal_private_room(self):
        return f"personal_user_private_room_{self.id}"

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "description": self.description,
            "profile_url": self.profile_url
        }

    def private_json(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "description": self.description,
            "channels": serialize_list(self.channels),
            "friends": serialize_list(self.friends)
        }

    def join_all_required_rooms(self):
        join_room(self.personal_private_room)
        for channel in self.channels:
            join_room(channel.room_id)

    def leave_all_required_rooms(self):
        leave_room(self.personal_private_room)
        for channel in self.channels:
            leave_room(channel.room_id)

    def updated(self):
        socketio.emit("user_private_data_changed", self.private_json(), room=self.personal_private_room)
        socketio.emit("user_public_data_changed", self.public_json(), room=self.personal_public_room)

    def __repr__(self):
        return '<User %r>' % self.username


class Channel(db.Model, Serializable):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), default="")
    description = db.Column(db.String(400), default="")
    members = db.relationship("ChannelMember",
                              backref='channel',
                              lazy='dynamic')
    messages = db.relationship("Message",
                               backref='channel',
                               lazy='dynamic')
    roles = db.relationship("ChannelRole",
                            backref="channel",
                            lazy=True)
    user_roles = db.relationship("UserRole",
                                 backref="channel",
                                 lazy="dynamic")

    @property
    def room_id(self):
        return f"channel_room_{self.id}"

    @property
    def personal_public_room(self):
        return f"personal_channel_public_room_{self.id}"

    @property
    def personal_private_room(self):
        return f"personal_channel_private_room_{self.id}"

    def get_member(self, user: User):
        results = list(filter(
            lambda mem: mem.user.id == user.id,
            self.members
        ))
        return None if len(results) == 0 else results[0]

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "roles": serialize_list(self.roles)
        }

    def updated(self):
        socketio.emit("channel_private_data_changed", self.private_json(), room=self.personal_private_room)
        socketio.emit("channel_public_data_changed", self.public_json(), room=self.personal_public_room)

    @staticmethod
    def make(creator: User, all_users: List[User]):
        new_channel = Channel()

        # init members
        members = list(map(
            lambda u: ChannelMember.make(u, new_channel),
            all_users
        ))
        new_channel.members = members

        # init roles:
        member_role = ChannelRole.create_member_role(new_channel)
        moderator_role = ChannelRole.create_moderator_role(new_channel)
        db.session.add(member_role)
        db.session.add(moderator_role)
        new_channel.roles.append(member_role)
        new_channel.roles.append(moderator_role)

        # set required roles to members
        for user in all_users:
            new_channel.user_roles.append(UserRole.make(user, member_role, new_channel))
        new_channel.user_roles.append(UserRole.make(creator, moderator_role, new_channel))

        # update channels for members:
        for user in all_users:
            user.channels.append(new_channel)

        db.session.add(new_channel)
        db.session.commit()

        return new_channel

    def __repr__(self):
        return f"<Channel {self.id}>"


class ChannelRole(db.Model, Serializable):
    __tablename__ = 'channel_role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(80), nullable=False)
    watch_channel_information_permission = db.Column(db.Boolean, default=False)
    watch_channel_members_permission = db.Column(db.Boolean, default=False)
    read_channel_permission = db.Column(db.Boolean, default=False)
    send_messages_permission = db.Column(db.Boolean, default=False)
    edit_channel_permission = db.Column(db.Boolean, default=False)

    user_roles = db.relationship("UserRole",
                                 backref="role",
                                 lazy="dynamic")
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

    @staticmethod
    def create_member_role(channel):
        return ChannelRole(
            role_name="Member",
            channel=channel,
            watch_channel_information_permission=True,
            watch_channel_members_permission=True,
            read_channel_permission=True,
            send_messages_permission=True
        )

    @staticmethod
    def create_moderator_role(channel):
        return ChannelRole(
            role_name="Moderator",
            channel=channel,
            edit_channel_permission=True
        )

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "role_name": self.role_name,
            "watch_channel_information_permission": self.watch_channel_information_permission,
            "watch_channel_members_permission": self.watch_channel_members_permission,
            "read_channel_permission": self.read_channel_permission,
            "send_messages_permission": self.send_messages_permission,
            "edit_channel_permission": self.edit_channel_permission
        }


class ChannelMember(db.Model, Serializable):
    __tablename__ = "channel_member"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

    @property
    def user_roles(self):
        return list(filter(
            lambda user_role: user_role.user.id == self.user.id,
            self.channel.user_roles
        ))

    @staticmethod
    def make(user: User, channel: Channel):
        member = ChannelMember(
            user_id=user.id,
            channel_id=channel.id
        )
        user.membership.append(member)
        channel.members.append(member)
        db.session.add(member)
        db.session.commit()
        return member

    def has_permission(self, permission_name: str) -> bool:
        assert hasattr(ChannelRole, permission_name)
        return any(map(
            lambda user_role: getattr(user_role.role, permission_name),
            self.user_roles))

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "user": self.user.public_json(),
            "channel": self.channel.public_json(),
            "user_roles": serialize_list(self.user_roles)
        }


class UserRole(db.Model, Serializable):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('channel_role.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

    @staticmethod
    def make(user: User, role: ChannelRole, channel: Channel):
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
            channel_id=channel.id
        )
        return user_role

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "user": self.user.public_json(),
            "role": self.role.public_json(),
            "channel": self.channel.public_json()
        }


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
