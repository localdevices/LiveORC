from django.db import models

from ..models import Site


class TimeSeries(models.Model):
    """
    temporary water level for sites used to provide water levels to uploaded videos
    """
    timestamp = models.DateTimeField(
        help_text="Date and time of water level value"
    )
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    h = models.FloatField("Water level", help_text="Value of water level in meter, referenced against local datum [m]", null=True, blank=True)
    q_05 = models.FloatField("Discharge 5%", help_text="River flow with probability of non-exceedance of 5% [m3/s]", null=True, blank=True)
    q_25 = models.FloatField("Discharge 25%", help_text="River flow with probability of non-exceedance of 25% [m3/s]", null=True, blank=True)
    q_50 = models.FloatField("Discharge median", help_text="Median river flow", null=True, blank=True)
    q_75 = models.FloatField("Discharge 75%", help_text="River flow with probability of non-exceedance of 75% [m3/s]", null=True, blank=True)
    q_95 = models.FloatField("Discharge 95%", help_text="River flow with probability of non-exceedance of 95% [m3/s]", null=True, blank=True)
    wetted_surface = models.FloatField(help_text="Wetted surface area with given water level [m2]", null=True, blank=True)
    wetted_perimeter = models.FloatField(help_text="Wetted perimeter with given water level [m]", null=True, blank=True)
    fraction_velocimetry = models.FloatField(help_text="Fraction of discharge resolved using velocimetry [-]", null=True, blank=True)
    # TODO: create link with videos, filtered on site, to add water level to those videos.

    class Meta:
        indexes = [models.Index(fields=['site', 'timestamp'])]
        verbose_name_plural = "time series"