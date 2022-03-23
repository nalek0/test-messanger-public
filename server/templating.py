from flask import render_template
from flask_login import current_user


def render_base_template(template: str, **kwargs):
    return render_template(template, client_user=current_user, **kwargs)
