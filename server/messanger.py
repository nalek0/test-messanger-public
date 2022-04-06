from flask import Blueprint, redirect, url_for, request, abort
from flask_login import login_required, current_user
from werkzeug import exceptions

from database import User, Channel, ChannelFabric
from templating import render_base_template

messanger = Blueprint("messanger", __name__,
                      url_prefix="/messanger",
                      template_folder="templates/messanger",
                      static_folder="static/messanger")


@messanger.route("/channel/<int:channel_id>")
@login_required
def channel(channel_id: int):
    current_channel = Channel.query.get(channel_id)
    if current_channel is not None and \
            current_channel.get_member(current_user).has_permission("read_channel_permission"):
        return render_base_template("channel.html", channel=current_channel)
    else:
        return abort(exceptions.Forbidden.code)


@messanger.route("/channel/<int:channel_id>/settings")
@login_required
def channel_settings(channel_id: int):
    current_channel = Channel.query.get(channel_id)
    if current_channel is not None and \
            current_channel.get_member(current_user).has_permission("watch_channel_members_permission"):
        return render_base_template("channel_settings.html", channel=current_channel)
    else:
        return abort(exceptions.Forbidden.code)
