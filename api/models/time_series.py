
from django.db import models
from django.apps import apps
import numpy as np

from api.models import BaseModel, Site


def get_closest_to_dt(queryset, timestamp):
    greater = queryset.filter(timestamp__gte=timestamp).order_by("timestamp").first()
    less = queryset.filter(timestamp__lte=timestamp).order_by("-timestamp").first()

    if greater and less:
        return greater if abs(greater.timestamp - timestamp) < abs(less.timestamp - timestamp) else less
    else:
        return greater or less


def get_str(value, dec=1):
    if value is None:
        return "-"
    else:
        return str(round(value, dec))


class TimeSeries(BaseModel):
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
    def save(self, *args, **kwargs):
        super(TimeSeries, self).save(*args, **kwargs)
        # try to associate a video with the time series
        Video = apps.get_model('api.Video')
        from ..models import VideoStatus
        videos_at_site = Video.objects.filter(
            camera_config__site__id=self.site.id
        ).filter(status=VideoStatus.NEW)
        if len(videos_at_site) != 0:
            # apparently there is a candidate time series record
            video_closest = get_closest_to_dt(videos_at_site, self.timestamp)
            # check if time diff is acceptable
            dt = np.abs(self.timestamp - video_closest.timestamp)
            if dt < video_closest.camera_config.allowed_dt:
                video_closest.time_series = self
                # video_closest.status = VideoStatus.QUEUE
                video_closest.save()

    class Meta:
        indexes = [models.Index(fields=['site', 'timestamp'])]
        verbose_name_plural = "time series"

    def __str__(self):
        return "{:s} h [m]: {:s}, Q [m3/s]: {:s}, f [-]: {:s}".format(
            self.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            get_str(self.h, 3),
            get_str(self.q_50, 2),
            get_str(self.fraction_velocimetry, 1)
        )