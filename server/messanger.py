from flask import Blueprint, redirect, url_for, request, abort
from flask_login import login_required, current_user
from werkzeug import exceptions

from templating import render_base_template
from database import User, Channel, ChannelRole, ChannelMember, db, ChannelFabric

messanger = Blueprint("messanger", __name__,
                      url_prefix="/messanger",
                      template_folder="templates/messanger",
                      static_folder="static/messanger")


@messanger.route("/make_channel", methods=["POST"])
@login_required
def create_channel():
    title = request.form["title"]
    description = request.form["description"]
    companions = request.form.get("companions", [])

    other_users = list(map(
        lambda companion_id: User.query.get(companion_id),
        companions
    ))
    if any(map(lambda el: el is None, other_users)):
        abort(exceptions.BadRequest.code)

    all_members = other_users + [current_user]
    new_channel = ChannelFabric(title, description, all_members, current_user).make()

    return redirect(url_for("messanger.channel", channel_id=new_channel.id))


@messanger.route("/channel/<int:channel_id>")
@login_required
def channel(channel_id: int):
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is not None and \
            current_channel.get_member(current_user).has_permission("read_channel_permission"):
        return render_base_template("channel.html", channel=current_channel)
    else:
        abort(exceptions.Forbidden.code)


@messanger.route("/channel/<int:channel_id>/settings")
@login_required
def channel_settings(channel_id: int):
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is not None and \
            current_channel.get_member(current_user).has_permission("watch_channel_members_permission"):
        return render_base_template("channel_settings.html", channel=current_channel)
    else:
        abort(exceptions.Forbidden.code)
