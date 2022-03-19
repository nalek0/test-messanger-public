from typing import List

from flask import Blueprint, \
    render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from sqlalchemy import or_, and_

from database import Channel, User, db

messanger = Blueprint("messanger", __name__,
                      url_prefix="/messanger",
                      template_folder="templates/messanger",
                      static_folder="static/messanger")

@messanger.route("/channels")
@messanger.route("/channels/<int:page>")
@login_required
def channels(page: int = 0):
    return render_template("channels.html", page=page, number_of_pages=1, channels=current_user.channels)


@messanger.route("/make_channel/<int:other_id>")
@login_required
def create_channel(other_id: int):
    other_user = User.query.get_or_404(other_id)

    new_channel = Channel()
    current_user.channels.append(new_channel)
    other_user.channels.append(new_channel)
    new_channel.members.append(current_user)
    new_channel.members.append(other_user)
    db.session.add(new_channel)
    db.session.commit()

    return redirect(url_for("messanger.channel", channel_id=new_channel.id))


@messanger.route("/channel/<int:channel_id>")
@login_required
def channel(channel_id: int):
    current_channel = Channel.query.get_or_404(channel_id)
    return render_template("channel.html",
                           channel=current_channel)
