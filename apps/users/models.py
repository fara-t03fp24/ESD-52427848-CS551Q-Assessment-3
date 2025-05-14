from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from apps.common.models import BaseModel
from apps.users.managers import CustomUserManager


class User(AbstractUser, BaseModel):
    """
    Custom user model for PrintCraft marketplace
    """
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Profile Picture',
        help_text='Upload a profile picture (optional)'
    )
    last_activity = models.DateTimeField(default=timezone.now)
    username = None  # Disable username field

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.email

    def get_full_name(self):
        """
        Return the user's full name or email if not set
        """
        if self.full_name:
            return self.full_name
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email

    @property
    def is_profile_complete(self):
        """
        Check if user has completed their profile
        """
        return bool(self.first_name and self.last_name and self.email)

    @property
    def has_shop(self):
        """
        Check if user has created their shop
        """
        return hasattr(self, 'shop')

    @property
    def is_seller(self):
        """
        A user is considered a seller only if they have a shop
        """
        return self.has_shop
