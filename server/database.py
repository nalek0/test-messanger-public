import datetime as datetime
from typing import Optional, List

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
    user_invitations = db.relationship('ChannelInvitation',
                                       backref='user',
                                       lazy=True)

    avatar_id = db.Column(db.Integer, nullable=True, default=None)
    avatar_big = db.Column(db.String(100), nullable=True, default=None)
    avatar_medium = db.Column(db.String(100), nullable=True, default=None)
    avatar_small = db.Column(db.String(100), nullable=True, default=None)

    def get_avatar_big_or(self, default: str) -> str:
        return self.avatar_big or default

    def get_avatar_medium_or(self, default: str) -> str:
        return self.avatar_medium or default

    def get_avatar_small_or(self, default: str) -> str:
        return self.avatar_small or default

    def set_avatar(self, data: dict) -> None:
        self.avatar_id = data["id"]
        self.avatar_big = data["thumbnails"]["512"]["url"]
        self.avatar_medium = data["thumbnails"]["128"]["url"]
        self.avatar_small = data["thumbnails"]["32"]["url"]

    @property
    def profile_url(self) -> str:
        return url_for("main.profile", username=self.username)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def personal_public_room(self) -> str:
        return f"personal_user_public_room_{self.id}"

    @property
    def personal_private_room(self) -> str:
        return f"personal_user_private_room_{self.id}"

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "description": self.description,
            "profile_url": self.profile_url,
            "avatar": {
                "big": self.avatar_big,
                "medium": self.avatar_medium,
                "small": self.avatar_small
            }
        }

    def private_json(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "description": self.description,
            "profile_url": self.profile_url,
            "avatar": {
                "big": self.avatar_big,
                "medium": self.avatar_medium,
                "small": self.avatar_small
            },
            "channels": serialize_list(self.channels),
            "friends": serialize_list(self.friends)
        }

    def join_all_required_rooms(self) -> None:
        join_room(self.personal_private_room)
        for channel in self.channels:
            join_room(channel.room_id)

    def leave_all_required_rooms(self) -> None:
        leave_room(self.personal_private_room)
        for channel in self.channels:
            leave_room(channel.room_id)

    def updated(self) -> None:
        socketio.emit("user_private_data_changed", self.private_json(), room=self.personal_private_room)
        socketio.emit("user_public_data_changed", self.public_json(), room=self.personal_public_room)

    def __repr__(self) -> str:
        return f"User username={self.username}>"


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
    default_role_id = db.Column(db.Integer)
    user_roles = db.relationship("UserRole",
                                 backref="channel",
                                 lazy="dynamic")
    member_invitations = db.relationship('ChannelInvitation',
                                         backref='channel',
                                         lazy='dynamic')

    @property
    def room_id(self) -> str:
        return f"channel_room_{self.id}"

    @property
    def personal_public_room(self) -> str:
        return f"personal_channel_public_room_{self.id}"

    @property
    def personal_private_room(self) -> str:
        return f"personal_channel_private_room_{self.id}"

    def get_member(self, user: User):
        results = list(filter(
            lambda mem: mem.user.id == user.id,
            self.members
        ))
        return None if len(results) == 0 else results[0]

    def add_member(self, user: User) -> None:
        if self.get_member(user) is None:
            member = ChannelMemberFabric(user, self).make()

            user.membership.append(member)
            user.channels.append(self)
            member_role = next(filter(lambda el: el.id == self.default_role_id, self.roles), None)
            self.user_roles.append(UserRoleFabric(user, member_role, self).make())
            self.members.append(member)

            db.session.add(member)
            db.session.commit()

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "roles": serialize_list(self.roles)
        }

    def updated(self) -> None:
        socketio.emit("channel_private_data_changed", self.private_json(), room=self.personal_private_room)
        socketio.emit("channel_public_data_changed", self.public_json(), room=self.personal_public_room)

    def __repr__(self) -> str:
        return f"<Channel id={self.id}, title={self.title}>"


class ChannelInvitation(db.Model, Serializable):
    __tablename__ = 'channel_invitation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column('channel_id', db.Integer, db.ForeignKey('channel.id'), nullable=False)

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "user": self.user.public_json(),
            "channel": self.channel.public_json(),
        }

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def use(self) -> None:
        self.channel.add_member(self.user)
        self.user.updated()
        self.channel.updated()
        self.delete()

    def __repr__(self) -> str:
        return f"<ChannelInvitation user={self.user}, channel={self.channel}>"


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


class UserRole(db.Model, Serializable):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('channel_role.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

    def public_json(self) -> dict:
        return {
            "id": self.id,
            "user": self.user.public_json(),
            "role": self.role.public_json(),
            "channel": self.channel.public_json()
        }


class ChannelMember(db.Model, Serializable):
    __tablename__ = "channel_member"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

    @property
    def user_roles(self) -> List[UserRole]:
        return list(filter(
            lambda user_role: user_role.user.id == self.user.id,
            self.channel.user_roles
        ))

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

    def __repr__(self) -> str:
        return f"<ChannelMember id={self.id}, user={self.user}, channel={self.channel}>"


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

    def __repr__(self) -> str:
        return f"<Message {self.id}>"


# Fabrics:
class ChannelFabric:
    def __init__(self,
                 title: str,
                 description: str,
                 other_users: List[User],
                 owner: User):
        self.title = title
        self.description = description
        self.other_users = other_users
        self.owner = owner

    def make(self) -> Channel:
        new_channel = Channel(
            title=self.title,
            description=self.description
        )

        # init members
        new_channel.members = [ChannelMemberFabric(self.owner, new_channel).make()]

        # init roles:
        channel_role_fabric = ChannelRoleFabric(new_channel)
        member_role = channel_role_fabric.create_member_role()
        moderator_role = channel_role_fabric.create_moderator_role()
        db.session.add(member_role)
        db.session.add(moderator_role)
        new_channel.roles.append(member_role)
        new_channel.roles.append(moderator_role)

        new_channel.default_role_id = member_role.id

        # set required roles to members
        new_channel.user_roles.append(UserRoleFabric(self.owner, member_role, new_channel).make())
        new_channel.user_roles.append(UserRoleFabric(self.owner, moderator_role, new_channel).make())

        # update channels for members:
        self.owner.channels.append(new_channel)

        db.session.add(new_channel)
        db.session.commit()

        # init default roles:
        member_role.default_for = new_channel
        new_channel.default_roles = [member_role]

        # send invitations
        for user in self.other_users:
            db.session.add(ChannelInvitation(user_id=user.id, channel_id=new_channel.id))
        db.session.commit()

        return new_channel


class ChannelRoleFabric:
    def __init__(self, channel: Channel):
        self.channel = channel

    def create_member_role(self) -> ChannelRole:
        return ChannelRole(
            role_name="Member",
            channel=self.channel,
            watch_channel_information_permission=True,
            watch_channel_members_permission=True,
            read_channel_permission=True,
            send_messages_permission=True
        )

    def create_moderator_role(self) -> ChannelRole:
        return ChannelRole(
            role_name="Moderator",
            channel=self.channel,
            edit_channel_permission=True
        )


class UserRoleFabric:
    def __init__(self,
                 user: User,
                 role: ChannelRole,
                 channel: Channel):
        self.user = user
        self.role = role
        self.channel = channel

    def make(self) -> UserRole:
        return UserRole(
            user_id=self.user.id,
            role_id=self.role.id,
            channel_id=self.channel.id
        )


class ChannelMemberFabric:
    def __init__(self,
                 user: User,
                 channel: Channel):
        self.user = user
        self.channel = channel

    def make(self) -> ChannelMember:
        member = ChannelMember(
            user_id=self.user.id,
            channel_id=self.channel.id
        )
        self.user.membership.append(member)
        self.channel.members.append(member)
        db.session.add(member)
        db.session.commit()
        return member
