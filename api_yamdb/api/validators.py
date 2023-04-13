import re

from rest_framework.exceptions import ValidationError
from users.models import User

username_pattern = re.compile(r'^[\w.@+-]+\Z')


def validate_username(value):
    if value.casefold() == 'me':
        raise ValidationError('Недопустимое имя пользователя')
    if not username_pattern.match(value):
        raise ValidationError(
            'Create a normal username please'
        )


def validate_email_exists(email):
    if User.objects.filter(email=email).exists():
        raise ValidationError(
            'Пользователь с такой почтой '
            'уже зарегестрирован'
        )


def validate_username_exists(username):
    if User.objects.filter(username=username).exists():
        raise ValidationError(
            'Пользователь c таким именем '
            'уже зарегестрирован'
        )


def validate_username_or_email_exists(username, email):
    validate_username_exists(username)
    validate_email_exists(email)
