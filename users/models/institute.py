from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from LiveORC.utils import choices


class Institute(models.Model):
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="institute"
    )
    name = models.CharField(_("Name"), max_length=255, help_text=_("Name of institute"))

    def __str__(self):
        return self.name

    def has_member(self, user):
        return self.members.filter(user=user).exists()

    def has_members(self):
        return self.members.exists()

    def add_member(self, user, role):
        """Add member to institute
        Args: user User, role RoleTypes
        """
        member = self.members.create(user=user, role=role)
        return member


class Member(models.Model):
    institute = models.ForeignKey(
        "Institute", related_name="members", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        get_user_model(), related_name="members", on_delete=models.CASCADE
    )
    role = models.CharField(
        choices=choices.TeamRole.choices, default=choices.TeamRole.MEMBER, max_length=32
    )

    def __str__(self):
        return f"{self.user} - {self.institute}"