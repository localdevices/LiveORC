from django.db import models
from django.utils import timezone
from ..models import Site



class Profile(models.Model):
    """
    Contains the river profile as a geojson
    """
    data = models.JSONField(help_text="GeoJSON fields containing Point (x,y,z) geometries that encompass a cross section")
    timestamp = models.DateTimeField("survey date", default=timezone.now)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    # TODO: change into a GeoJSON field (using GeoDjango)
