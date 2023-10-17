from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from LiveORC.utils.models.base import BaseModel
from django.apps import apps
# from ..models import Institute


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
    institute = models.ForeignKey(
        'Institute',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
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

    def is_company_member(self, institute):
        return self.members.filter(institute=institute).exists()

