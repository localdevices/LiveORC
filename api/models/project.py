from django.contrib.auth import get_user_model
from django.db import models

from api.models import BaseModel


class Project(BaseModel):
    """
    Project that holds together one or several videos at different sites (for surveys)
    """
    name = models.CharField(max_length=100, help_text="Name of project")
    description = models.TextField(
        help_text="Summary of the project details, e.g. sites, client, purpose, intended outcome"
    )
    # user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)

