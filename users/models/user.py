from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from users.models.base import BaseModel


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.is_active = True
        user.is_verified = False
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    name = models.CharField(_("full Name"), max_length=100, blank=True, null=True)
    email = models.EmailField(_("email Address"), max_length=255, unique=True)

    is_staff = models.BooleanField(
        _("Staff Status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site"))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        app_label = 'users'
        db_table = "auth_user"

    def __str__(self):
        return self.get_fullname()

    def get_fullname(self):
        return self.name if self.name else self.email

    def is_institute_member(self, institute):
        return self.members.filter(institute=institute).exists()

    def get_memberships(self):
        return self.members.all()

    def get_membership_institutes(self):
        memberships = self.members.all()
        return [m.institute for m in memberships]

    def get_owned_institute_memberships(self):
        """Get the memberships with institutes owned by current user"""
        memberships = self.members.all()
        return memberships.filter(institute__owner=self)

