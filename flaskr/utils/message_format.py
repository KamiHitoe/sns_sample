
from flask import url_for
from flask_login import current_user
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


def make_old_message_format(user, messages):
    message_tag = ''
    for message in messages[::-1]:
        if message.from_user_id == int(current_user.get_id()):
            message_tag += '<div class="col-md-2">'

            if current_user.picture_path:
                message_tag += f'<img class="user-image-mini" src="{url_for("static", filename=current_user.picture_path)}">'
            message_tag += f'<p>{current_user.username}</p></div>'

            message_tag += '<div class="speech-bubble-self col-md-4">'
            for splitted_message in replace_newline(message.message):
                message_tag += f'<p>{urlize(splitted_message, target=True)}</p>'
            message_tag += f'<p>{message.create_at.strftime("%H:%M")}</p></div>'

            message_tag += f'<div id="self-message-tag-{message.id}" class="col-md-2">'
            if message.is_checked:
                message_tag += '<p>既読</p>'
            message_tag += '</div><div class="col-md-4"></div>'

        else:
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
