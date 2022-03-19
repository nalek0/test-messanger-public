from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

channel_association_table = db.Table(
    'channel_association',
    db.Column('user.id', db.ForeignKey('user.id')),
    db.Column('channel.id', db.ForeignKey('channel.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    channels = db.relationship("Channel",
                               secondary=channel_association_table,
                               backref="members")

    def __repr__(self):
        return '<User %r>' % self.username

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Channel(db.Model):
    __tablename__ = 'channel'
    id = db.Column(db.Integer, primary_key=True)

    # members = ...

    def __repr__(self):
        return f"<Channel {self.id}>"
