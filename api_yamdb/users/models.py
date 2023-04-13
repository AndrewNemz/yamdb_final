from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model
    role field value gives extra permissions on the API
    staff is always admin
    """
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    USER_ROLES = (
        (ADMIN, 'Администратор'),
        (USER, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
    )

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль', max_length=20,
        choices=USER_ROLES,
        default=USER
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )

    confirmation_code = models.CharField(max_length=10, blank=True, null=True)

    @property
    def is_admin(self):
        """Is the user a member of staff?."""
        return (self.role == User.ADMIN) or self.is_staff

    @property
    def is_user(self):
        """Is the user a member of staff?."""
        return self.role == User.USER

    @property
    def is_moderator(self):
        """Is the user a member of staff?."""
        return self.role == User.MODERATOR
