from django.db import models
import pyorc
from api.models import BaseInstituteModel


class Recipe(BaseInstituteModel):
    """
    Contains settings to process videos
    """
    name = models.CharField(max_length=100, help_text="Recognizable unique name for your recipe")
    data = models.JSONField(help_text="JSON formatted recipe for processing videos. See https://localdevices.github.io/pyorc/user-guide/cli.html")
    version = models.CharField(max_length=15, blank=True, default=pyorc.__version__, editable=False)
