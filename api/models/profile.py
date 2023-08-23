from django.db import models
from django.core.exceptions import ValidationError
import pyorc


class Profile(models.Model):
    """
    Contains the river profile as a geojson
    """
    data = models.JSONField(help_text="GeoJSON fields containing Point (x,y,z) geometries that encompass a cross section")
    # TODO: change into a GeoJSON field (using GeoDjango)

    def clean(self):
        super().clean()
        try:
            pyorc.CameraConfig(**self.data)
            # see if you can make a camera config object
        except BaseException as e:
            raise ValidationError(f"Problem with Camera Configuration: {e}")

