
from flask import url_for
from jinja2.utils import urlize
from flaskr.utils.template_filters import replace_newline


def make_message_format(user, messages):
    message_tag = ''
    for message in messages:
        message_tag += '<div class="col-md-6"></div>'

        message_tag += '<div class="speech-bubble-dest col-md-4">'
        for splitted_message in replace_newline(message.message):
            message_tag += f'<p>{urlize(splitted_message, target=True)}</p>'
        message_tag += f'<p>{message.create_at.strftime("%H:%M")}</p></div>'

        message_tag += '<div class="col-md-2">'
        if user.picture_path:
            message_tag += f'<img class="user-image-mini" src="{url_for("static", filename=user.picture_path)}">'
        message_tag += f'<p>{user.username}</p></div>'
    return message_tag
