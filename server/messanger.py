from flask import Blueprint, \
    render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user

from database import Channel, User, db

messanger = Blueprint("messanger", __name__,
                      url_prefix="/messanger",
                      template_folder="templates/messanger",
                      static_folder="static/messanger")


@messanger.route("/channels")
@messanger.route("/channels/<int:page>")
@login_required
def channels(page: int = 0):
    return render_template("channels.html", page=page, number_of_pages=1, client_user=current_user)


@messanger.route("/make_channel", methods=["POST"])
@login_required
def create_channel():
    companions = request.form.get("companions")
    if companions is None:
        return abort(400)

    other_users = list(map(
        lambda companion: User.query.get_or_404(companion),
        companions
    ))

    new_channel = Channel()
    current_user.channels.append(new_channel)
    for user in other_users:
        user.channels.append(new_channel)

    new_channel.members.append(current_user)
    for user in other_users:
        new_channel.members.append(user)

    db.session.add(new_channel)
    db.session.commit()

    return redirect(url_for("messanger.channel", channel_id=new_channel.id))


@messanger.route("/channel/<int:channel_id>")
@login_required
def channel(channel_id: int):
    current_channel = Channel.query.get_or_404(channel_id)
    return render_template("channel.html",
                           channel=current_channel)
