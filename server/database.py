from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_user = db.Column(db.Integer, nullable=False)
    second_user = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Channel {self.id}>"
