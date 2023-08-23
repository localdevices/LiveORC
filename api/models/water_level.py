from django.db import models

from ..models import Site


class WaterLevel(models.Model):
    """
    temporary water level for sites used to provide water levels to uploaded videos
    """
    timestamp = models.DateTimeField(
        blank=True,
        help_text="Date and time of water level value"
    )
    value = models.FloatField(help_text="Value of water level in meter, referenced against local datum")
    # TODO: create link with videos, filtered on site, to add water level to those videos.
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
