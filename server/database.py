import datetime as datetime

from flask import url_for
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from server.serializable import Serializable

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

    friends = db.relationship('User',
                              secondary=user_friendship_association_table,
                              primaryjoin=(user_friendship_association_table.c.user_id == id),
                              secondaryjoin=(user_friendship_association_table.c.friend_id == id),
                              lazy='dynamic')

    def profile_url(self):
        return url_for("main.profile", username=self.username)

    def json(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "description": self.description
        }

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return '<User %r>' % self.username


class Channel(db.Model, Serializable):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)
    # members: List[User]
    messages = db.relationship("Message", backref='channel', lazy=True)

    def room_id(self):
        return f"channel_room_{self.id}"

    def has_permissions_to_read(self, user: User) -> bool:
        return user in self.members

    def json(self) -> dict:
        return {
            "id": self.id
        }

    def __repr__(self):
        return f"<Channel {self.id}>"


class Message(db.Model, Serializable):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def json(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "datetime": str(self.datetime),
            "channel": self.channel.json(),
            "author": self.author.json(),
        }

    def __repr__(self):
        return f"<Message {self.id}>"
