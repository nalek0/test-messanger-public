from typing import List

from flask import Blueprint, \
    render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from database import Channel, User, db

messanger = Blueprint("messanger", __name__,
                      url_prefix="/messanger",
                      template_folder="templates/messanger",
                      static_folder="static/messanger")


def get_all_users_channels(user1: User, user2: User):
    return Channel.query.filter(
        or_(
            and_(
                Channel.first_user.like(user1.username),
                Channel.second_user.like(user2.username)
            ),
            and_(
                Channel.first_user.like(user1.username),
                Channel.second_user.like(user2.username)
            )
        )
    )


def get_all_user_channels(user: User):
    return Channel.query.filter(
        or_(
            Channel.first_user.like(current_user.username),
            Channel.second_user.like(current_user.username)
        )
    )


def get_all_channels(page: int = 0, page_size: int = 10) -> List[Channel]:
    query = get_all_user_channels(current_user)
    query.offset(page_size * page)
    query.limit(page_size)
    return query.all()


@messanger.route("/channels")
@messanger.route("/channels/<int:page>")
@login_required
def channels(page: int = 0):
    number_on_page = 10
    number_of_pages = (get_all_user_channels(current_user).count() + number_on_page - 1) // number_on_page
    user_channels = get_all_channels(page, number_on_page)
    return render_template("channels.html", page=page, number_of_pages=number_of_pages, channels=user_channels)


@messanger.route("/make_channel/<int:other_id>")
@login_required
def create_channel(other_id: int):
    other = User.query.get_or_404(other_id)
    ch = get_all_users_channels(current_user, other).first()
    if ch is not None:
        return redirect(url_for("messanger.channel", channel_id=ch.id))

    new_channel = Channel(first_user=current_user.id, second_user=other.id)
    db.session.add(new_channel)
    db.session.commit()

    return redirect(url_for("messanger.channel", channel_id=new_channel.id))


@messanger.route("/channel/<int:channel_id>")
@login_required
def channel(channel_id: int):
    current_channel = Channel.query.get_or_404(channel_id)
    first_user = User.query.get_or_404(current_channel.first_user)
    second_user = User.query.get_or_404(current_channel.second_user)
    return render_template("channel.html",
                           channel=current_channel,
                           first_user=first_user,
                           second_user=second_user)
