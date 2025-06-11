from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True "
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True"
            )

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, error_messages={
        "unique": _("A user with that email already exists")
    })
    username = models.CharField(blank=True, null=True, default=None, max_length=10)
    telegram_chat_id = models.CharField(max_length=64, blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="user_user_user_permissions",
        related_query_name="user",
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email
    
    objects = CustomUserManager()