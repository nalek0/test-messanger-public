from typing import List

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from database import Channel, User

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
    number_of_pages = (get_all_user_channels().count() + number_on_page - 1) // number_on_page
    user_channels = get_all_channels(page, number_on_page)
    return render_template("channels.html", page=page, number_of_pages=number_of_pages, channels=user_channels)


@messanger.route("/channel/<int:channel_id>")
@login_required
def channel(channel_id: int):
    # TODO
    pass
