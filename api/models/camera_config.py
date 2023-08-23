from django.db import models
from django.core.exceptions import ValidationError
from ..models import Site, Server, Recipe, Profile

import pyorc

class CameraConfig(models.Model):
    """
    Contains JSON with a full camera configuration
    """
    def __str__(self):
        return f"{self.name} at {self.site.name}"

    name = models.CharField(max_length=100, help_text="Recognizable unique name for the camera configuration")
    data = models.JSONField(help_text="JSON fields containing a camera configuration, see https://localdevices.github.io/pyorc/user-guide/camera_config/index.html for setup instructions")
    start_date = models.DateTimeField("start validity date", auto_now_add=True)
    end_date = models.DateTimeField("end validity date", null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    version = models.CharField(max_length=15, blank=True, default=pyorc.__version__, editable=False)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO also connect to server
    # TODO connect to recipe and profile (where necessary)

    def clean(self):
        super().clean()
        try:
            pyorc.CameraConfig(**self.data)
            # see if you can make a camera config object
        except BaseException as e:
            raise ValidationError(f"Problem with Camera Configuration: {e}")

