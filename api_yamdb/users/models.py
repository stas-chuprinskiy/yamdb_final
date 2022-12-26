from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )

    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.CharField(
        max_length=50, choices=ROLES, default=USER, verbose_name='Role'
    )
    bio = models.TextField(blank=True, null=True, verbose_name='Biography')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        constraints = (
            models.CheckConstraint(
                name='not_equal_username_me',
                check=~models.Q(username='me'),
            ),
        )

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser
