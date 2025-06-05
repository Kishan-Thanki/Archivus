from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import gettext_lazy as _
from .degree_level import DegreeLevel
from .program import Program


# --- 1. Custom User Manager ---
# This manager will handle creating users and superusers.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


# --- 2. Corrected User Model ---
# Inherit from AbstractBaseUser and PermissionsMixin
class User(AbstractBaseUser, PermissionsMixin):
    GOOGLE = 'google'
    FACEBOOK = 'facebook'
    GITHUB = 'github'

    OAUTH_PROVIDERS = [
        (GOOGLE, 'Google'),
        (FACEBOOK, 'Facebook'),
        (GITHUB, 'GitHub'),
    ]

    # --- Authentication fields ---
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255, blank=True, null=True)

    # OAuth fields
    oauth_provider = models.CharField(max_length=50, choices=OAUTH_PROVIDERS, blank=True, null=True)
    oauth_id = models.CharField(max_length=255, blank=True, null=True)

    # Academic information
    degree_level = models.ForeignKey(DegreeLevel, on_delete=models.SET_NULL, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, blank=True, null=True)
    enrollment_year = models.PositiveIntegerField(blank=True, null=True)

    # Points system
    points = models.IntegerField(default=0)

    # --- Required fields for AbstractBaseUser and PermissionsMixin ---
    # These are critical for Django's permission system and admin panel.
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. '
                    'Unselect this instead of deleting accounts.'),
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    # --- Manager and Field Definitions ---
    objects = CustomUserManager() # Assign your custom manager

    USERNAME_FIELD = 'email' # <--- IMPORTANT: Tells Django to use 'email' as the unique identifier for authentication
    REQUIRED_FIELDS = ['username'] # <--- IMPORTANT: Fields required when creating a user via createsuperuser

    # --- Custom methods for password handling (as you had them) ---
    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)
        self._password = raw_password # Store for saving if needed

    def check_password(self, raw_password):
        if not self.password_hash:
            return False
        return check_password(raw_password, self.password_hash)

    # --- Required methods for custom user model (from AbstractBaseUser) ---
    # These are no longer @property but actual methods or handled by mixins
    # get_full_name() and get_short_name() are commonly added for admin/display
    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    # has_perm, has_module_perms are provided by PermissionsMixin


    def __str__(self):
        return self.email # Often better to use email as string representation for email-based login

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")