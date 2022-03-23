from flask import Blueprint, redirect, url_for, request, abort
from flask_login import login_required, current_user
from werkzeug import exceptions

from database import Channel, User, db, \
    AdminRole, ModeratorRole, MemberRole
from templating import render_base_template
import permissions

messanger = Blueprint("messanger", __name__,
                      url_prefix="/messanger",
                      template_folder="templates/messanger",
                      static_folder="static/messanger")


@messanger.route("/make_channel", methods=["POST"])
@login_required
def create_channel():
    companions = request.form.get("companions")
    if companions is None:
        return abort(exceptions.BadRequest.code)

    other_users = list(map(
        lambda companion: User.query.get(companion),
        companions
    ))
    if any(map(lambda el: el is None, other_users)):
        abort(exceptions.BadRequest.code)

    new_channel = Channel()

    # adding channel to list of user channels
    current_user.channels.append(new_channel)
    for user in other_users:
        user.channels.append(new_channel)

    # Adding members to channel
    new_channel.members.append(current_user)
    for user in other_users:
        new_channel.members.append(user)

    # Adding permissions to members
    AdminRole.set_permissions_for(new_channel, current_user)
    for user in other_users:
        MemberRole.set_permissions_for(new_channel, user)

    db.session.add(new_channel)
    db.session.commit()

    return redirect(url_for("messanger.channel", channel_id=new_channel.id))


@messanger.route("/channel/<int:channel_id>")
@login_required
def channel(channel_id: int):
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is not None and \
            current_channel\
            .get_user_permission(current_user)\
            .has_permission(permission=permissions.READ_CHANNEL):
        return render_base_template("channel.html", channel=current_channel)
    else:
        abort(exceptions.Forbidden.code)


@messanger.route("/channel/<int:channel_id>/members")
@login_required
def channel_members(channel_id: int):
    current_channel: Channel = Channel.query.get(channel_id)
    if current_channel is not None and \
            current_channel\
            .get_user_permission(current_user)\
            .has_permission(permission=permissions.WATCH_CHANNEL_MEMBERS):
        return render_base_template("channel_members.html", channel=current_channel)
    else:
        abort(exceptions.Forbidden.code)
