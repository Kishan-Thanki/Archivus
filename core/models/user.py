import logging

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.utils import timezone

from .base import TimeStampedModel
from .program import Program
from .degree_level import DegreeLevel

logger = logging.getLogger(__name__)

class UserRole(models.TextChoices):
    ADMIN = "Administrators", "Administrator"
    STAFF = "Staff", "Staff"
    STUDENT = "Students", "Student"
    ACADEMIC_MANAGER = "Academic Managers", "Academic Manager"
    DOCUMENT_REVIEWER = "Document Reviewers", "Document Reviewer"

class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        try:
            student_group = Group.objects.get(name=UserRole.STUDENT)
            user.groups.add(student_group)
        except Group.DoesNotExist:
            logger.warning(f"Group '{UserRole.STUDENT}' does not exist. Please create it.")
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(email, username, password, **extra_fields)  #

        try:
            admin_group = Group.objects.get(name=UserRole.ADMIN)
            user.groups.add(admin_group)
        except Group.DoesNotExist:
            logger.warning(f"Group '{UserRole.ADMIN}' does not exist. Please create it.")

        try:
            staff_group = Group.objects.get(name=UserRole.STAFF)
            user.groups.add(staff_group)
        except Group.DoesNotExist:
            logger.warning(f"Group '{UserRole.STAFF}' does not exist. Please create it.")

        return user

class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    oauth_provider = models.CharField(max_length=50, blank=True, null=True)
    oauth_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    degree_level = models.ForeignKey(DegreeLevel, on_delete=models.SET_NULL, null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True)
    enrollment_year = models.PositiveIntegerField(blank=True, null=True)
    points = models.IntegerField(default=0)

    is_banned = models.BooleanField(
        default=False,
        help_text="Designates whether this user has been banned and should not be granted access."
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email