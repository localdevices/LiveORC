from django.db import models


class TeamRole(models.TextChoices):
    OWNER = "owner", "Owner"
    MEMBER = "member", "Member"