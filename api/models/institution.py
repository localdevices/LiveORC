from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from LiveORC.utils import choices


class Institution(models.Model):
    owner = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="institution"
    )
    name = models.CharField(_("Name"), max_length=255, help_text=_("Name of institution"))

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    institution = models.ForeignKey(
        "Institution", related_name="teams", on_delete=models.CASCADE
    )
    member = models.ForeignKey(
        get_user_model(), related_name="teams", on_delete=models.CASCADE
    )
    role = models.CharField(
        choices=choices.TeamRole.choices, default=choices.TeamRole.MEMBER, max_length=32
    )

    def __str__(self):
        return f"{self.member} - {self.institution}"