from django.db import models
from django.dispatch import receiver
from .models import TimeSeries, Video
import numpy as np
from datetime import timedelta
from .models.video import get_closest_to_dt, VideoStatus
from .models import Task

@receiver(models.signals.post_save, sender=TimeSeries)
def timeseries_foreignkey_video(sender, instance, **kwargs):
    """
    Signal processing triggered when a time series instance is added. If the time series contains a water level
    then it is investigated if there is a Video instance for the same site, that does not yet have a time series
    instance with a water level within the allowed time difference.

    Each time series instance should only be associated with one single video.

    Parameters
    ----------
    sender : model or django sender
    instance : models.TimeSeries
        instance after saving
    kwargs : remainder kwargs, not used.

    Returns
    -------

    """
    # first check if the instance has a water level. If not, then don't bother.
    if instance.h is None:
        return
    # get the site nr of the TimeSeries instance
    site_id = instance.site.id

    # retrieve the video objects for the Site instance that DO NOT yet have a time series associated.
    video_at_site = Video.objects.filter(
        camera_config__site=site_id
    )
    # also check if the time series instance is not already used by any video
    if len(video_at_site.filter(time_series__pk=instance.id)) == 1:
        return

    video_no_ts = video_at_site.filter(time_series=None)
    # do we have any videos with missings, if no, then return
    if len(video_no_ts) == 0:
        # nothing to be done, return
        return
    video1 = video_no_ts.filter(
        timestamp__lte=instance.timestamp
    ).order_by(
        'timestamp'
    ).first()
    video2 = video_no_ts.filter(
        timestamp__gte=instance.timestamp
    ).order_by(
        '-timestamp'
    ).first()
    videos = [video1, video2]
    videos = list(filter(lambda item: item is not None, videos))
    # assess a closest in time time stamp between them
    # if the closest in time has a time diff < camera_config.allowed_dt, they'll be matched against each other
    # and the video instance updated.
    test_time_diff = timedelta(seconds=86400)
    video_idx = -1
    if len(videos) > 0:
        for n, video in enumerate(videos):
            dt = np.abs(video.timestamp - instance.timestamp)
            if dt < test_time_diff and dt < video.camera_config.allowed_dt:
                test_time_diff = dt
                video_idx = n

        if video_idx != -1:
            # assign the current time series instance on video
            video = videos[video_idx]
            video.time_series = instance
            # store the assigned value
            video.save()
#

@receiver(models.signals.post_save, sender=Video)
def video_process(sender, instance, **kwargs):
    """
    Signal processing triggered when Video is altered. Only when a water level is present, and status is NEW then
    a process should be autonomously started.

    Here only the formation and triggering of a task process is organized. The logic of that task and what it exactly
    does is organized in the task model.

    Parameters
    ----------
    sender : model or django sender
    instance : models.Video
        instance after saving
    kwargs : remainder kwargs, not used.

    Returns
    -------

    """
    if instance.time_series is None:
        return
    if instance.status == VideoStatus.NEW and instance.time_series.q_50 is None:
        # apparently this is a new video and it has a water level, but no flow yet.
        # create a new task, associated with the video
        # assemble a task context
        #

        raise NotImplementedError
