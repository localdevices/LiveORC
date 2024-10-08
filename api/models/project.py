from django.db import models

from api.models import BaseInstituteModel


class Project(BaseInstituteModel):
    """
    Project that holds together one or several videos at different sites (for surveys)
    """
    name = models.CharField(max_length=100, help_text="Name of project")
    description = models.TextField(
        help_text="Summary of the project details, e.g. sites, client, purpose, intended outcome"
    )
