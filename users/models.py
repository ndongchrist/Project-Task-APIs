import uuid
from django.utils.translation import gettext_lazy as _

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django_extensions.db.models import TimeStampedModel, ActivatorModel
from .managers import UserManager


# Create your models here.
class ProjectAPIBaseModel(TimeStampedModel, ActivatorModel):
    """
    Name: ProjectAPIBaseModel
    Description: Abstract base model providing a UUID primary key, soft deletion, and metadata for all models.
    Author: fotsingtchoupe1@gmail.com
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        null=False,
        blank=False,
        unique=True,
        primary_key=True,
        editable=False
    )
    is_deleted = models.BooleanField(default=False, help_text=_("Marks the record as deleted without removing it."))
    metadata = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text=_("Stores additional metadata in JSON format.")
    )
    
    class Meta:
        abstract = True
        
        
class User(ProjectAPIBaseModel, PermissionsMixin, AbstractBaseUser):
    """
    Name: User
    Description: Custom user model with email as the unique identifier and role-based flags.
    Author: fotsingtchoupe1@gmail.com
    """
    email = models.EmailField(
        _("email address"),
        blank=False,
        null=False,
        unique=True,
        error_messages={"unique": _("A user with that email already exists.")}
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)
    phone = models.CharField(_("phone number"), max_length=20, blank=True, null=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site.")
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active. Unselect instead of deleting accounts.")
    )
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_("Designates that this user has all permissions without explicitly assigning them.")
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text=_("User's IP address."))

    # Authentication settings
    username = None
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def has_perm(self, perm, obj=None):
        """Check if the user has a specific permission."""
        return True  # Simplified for superusers; adjust based on your needs

    def clean(self):
        """Normalize email before saving."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.fullname

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split("@")[0]

    def __str__(self):
        return self.email