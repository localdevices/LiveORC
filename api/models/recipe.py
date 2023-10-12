from django.db import models
from django.core.exceptions import ValidationError
import pyorc


class Recipe(models.Model):
    """
    Contains settings to process videos
    """
    name = models.CharField(max_length=100, help_text="Recognizable unique name for your recipe")
    data = models.JSONField(help_text="JSON formatted recipe for processing videos. See https://localdevices.github.io/pyorc/user-guide/cli.html")
    version = models.CharField(max_length=15, blank=True, default=pyorc.__version__, editable=False)
