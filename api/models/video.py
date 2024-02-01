from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import mark_safe
from django.core.files.base import ContentFile
from PIL import Image
import io
import mimetypes
import os
import cv2
import numpy as np
from django.conf import settings

from api.models import BaseModel, CameraConfig, Project, TimeSeries

VIDEO_EXTENSIONS = ["MOV", "MKV", "MP4", "AVI", "M4V"]


def add_frame_to_model(video_field, img_field, frame_nr=0, suffix="", thumb=False):
    """
    adds an image to a model from a file containing a video
    Inspired by https://stackoverflow.com/questions/23922289/django-pil-save-thumbnail-version-right-when-image-is-uploaded

    Parameters
    ----------
    video_field : models.FileField
        field in which video file is stored
    img_field : models.Image
        field in which image must be stored
    frame_nr : int
        frame number to extract
    suffix : str
        suffix name for file naming
    thumb : boolean
        Set to True to resize the image, settings.THUMBSIZE is used for the size settings
    """
    if "FieldFile" in repr(video_field):
        # a video is passed, so use opencv to get the key frame
        cap = cv2.VideoCapture(video_field.path)
        if frame_nr != 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_nr)
        res, image = cap.read()
    elif "ImageFieldFile" in repr(video_field):
        image = cv2.imread(video_field.path)
    # turn into RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_name, video_extension = os.path.splitext(os.path.basename(video_field.name))
    img_extension = ".jpg"
    FTYPE = 'JPEG'
    img_filename = img_name + suffix + img_extension
    # Save thumbnail to in-memory file as StringIO
    img = Image.fromarray(image, "RGB")
    if thumb:
    # thumb = Image.fromarray(image, "RGB")
        img.thumbnail((settings.THUMBSIZE, settings.THUMBSIZE), Image.LANCZOS)
    temp_img = io.BytesIO()
    img.save(temp_img, FTYPE)
    temp_img.seek(0)

    # set save=False, otherwise it will run in an infinite loop
    img_field.save(img_filename, ContentFile(temp_img.read()), save=False)
    temp_img.close()


def get_closest_to_dt(queryset, timestamp):
    greater = queryset.filter(timestamp__gte=timestamp).order_by("timestamp").first()
    less = queryset.filter(timestamp__lte=timestamp).order_by("-timestamp").first()

    if greater and less:
        return greater if abs(greater.timestamp - timestamp) < abs(less.timestamp - timestamp) else less
    else:
        return greater or less


def get_video_path(instance, filename):
    _, ext = os.path.splitext(filename)
    end_point = os.path.join(
        "videos",
        str(instance.camera_config.site_id),
        instance.timestamp.strftime("%Y%m%d"),
        instance.timestamp.strftime("%Y%m%dT%H%M%S") + ext
    )
    return end_point

def get_thumb_path(instance, filename):
    end_point = os.path.join(
        "thumb",
        str(instance.camera_config.site.id),
        instance.timestamp.strftime("%Y%m%d"),
        filename
    )
    return end_point

def get_keyframe_path(instance, filename):
    end_point = os.path.join(
        "keyframe",
        str(instance.camera_config.site.id),
        instance.timestamp.strftime("%Y%m%d"),
        filename
    )
    return end_point
"http://0.0.0.0:8000/admin/api/video/31/actions/toolfunc/"
def get_task_run(id):
    uri = reverse('admin:api_video_actions', args=([str(id), "toolfunc"]))
    return mark_safe(
        f"""<a href="{uri}"><i class="fa-solid fa-circle-play"></i></button> Click to queue
"""
    )


class VideoStatus(models.IntegerChoices):
    NEW = 1, "New video"
    QUEUE = 2, "Waiting for processing"
    TASK = 3, "Being processed"
    DONE = 4, "Finished"
    ERROR = 5, "Error occurred"


class Video(models.Model):
    """
    Video object with water level and flow information
    """
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # we use a uuid to ensure the name is and remain unique and can be used for file naming
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Date and time on which video record is created"
    )
    timestamp = models.DateTimeField(
        null=False,
        help_text="Data and time on which video was taken. If not provided by the user, this is taken from the file's time stamp"
    )
    file = models.FileField(
        upload_to=get_video_path,
        validators=[FileExtensionValidator(allowed_extensions=VIDEO_EXTENSIONS)],
        null=True,
    )
    keyframe = models.ImageField(
        upload_to=get_keyframe_path,
        help_text="Extracted frame for user contextual understanding or for making camera configurations",
        editable=False,
        max_length=254
    )
    image = models.ImageField(
        upload_to=get_video_path,
        help_text="Image showing the results of a velocimetry analysis",
        null=True,
        # max_length=254
    )
    thumbnail = models.ImageField(
        upload_to=get_thumb_path,
        help_text="Thumbnail frame for list views",
        editable=False
    )
    status = models.PositiveSmallIntegerField(
        choices=VideoStatus.choices,
        default=VideoStatus.NEW,
        # editable=False,
        help_text="Status of processing"
    )
    camera_config = models.ForeignKey(CameraConfig, on_delete=models.CASCADE)
    time_series = models.OneToOneField(TimeSeries, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        # default=get_current_user,
        editable=False
    )

    def save(self, *args, **kwargs):
        # move the file field to a separate variable temporarily.
        # This is in order to first get an ID on the video instance (otherwise video would be stored in a
        # folder called 'None'
        if not(self.pk):
            new_file = True
        else:
            new_file = False
        if new_file:
            file = self.file
            self.file = None

        super(Video, self).save(*args, **kwargs)
        if new_file:
            # now store the video
            self.file = file
            super(Video, self).save(*(), **{})
            if not(self.make_frames()):
                raise Exception('Could not create keyframe - is the file type valid?')
            # now check for a water level series
            if self.time_series is not None:
                return
            # look for time series instances that are for the same site and not yet associated with a video
            ts_at_site = TimeSeries.objects.filter(
                site=self.camera_config.site
            ) # TODO: exclude time series records that are already used by another video ....filter(
            #     video__time_series__ne=...
            if len(ts_at_site) != 0:
                # apparently there is a candidate time series record
                ts_closest = get_closest_to_dt(ts_at_site, self.timestamp)
                # check if time diff is acceptable
                dt = np.abs(self.timestamp - ts_closest.timestamp)
                if dt < self.camera_config.allowed_dt:
                    self.time_series = ts_closest
            super(Video, self).save(*(), **{})


    def make_frames(self):
        """
        make frame and thumbnail
        """
        if self.file:
            # extract one frame and save that as a keyframe
            add_frame_to_model(self.file, self.keyframe)
            add_frame_to_model(self.file, self.thumbnail, suffix="_thumb", thumb=True)
        else:
            # only add a thumbnail in this case
            add_frame_to_model(self.image, self.thumbnail, suffix="_thumb", thumb=True)
        return True

    def make_thumbnail(self):

        raise NotImplementedError


    @property
    def thumbnail_preview(self):
        if self.thumbnail:
            height = int(settings.THUMBSIZE) / 2
            try:
                width = int((self.thumbnail.width / self.thumbnail.height) * height)
            except:
                return mark_safe("File missing")
                # width = height * 1.5
            return mark_safe('<img src="{}" width="{}" height="{}" />'.format(self.thumbnail.url, width, height))
        return mark_safe("Nope sorry")

    @property
    def is_ready_for_task(self):
        if not(self.time_series):
            return False
        return self.status == VideoStatus.NEW and self.time_series.q_50 is None and self.time_series.h is not None

    @property
    def video_preview(self):
        height = int(300)
        width = int((self.keyframe.width / self.keyframe.height) * height)
        uri = reverse('api:site-video-playback', args=([str(self.camera_config.site.id), str(self.id)]))
        mimetype, _ = mimetypes.guess_type(self.file.name)

        if self.file:
            return mark_safe(
                '<video src="{}" width="{}" height="{}" type={} controls preload="none"/>'.format(
                    uri,
                    width,
                    height,
                    mimetype
                )
            )
        return ""

    @property
    def image_preview(self):
        height = int(300)
        if self.image:
            if os.path.isfile(self.image.url):
                width = int((self.image.width / self.image.height) * height)
                return mark_safe('<img src="{}" width="{}" height="{}" />'.format(self.image.url, width, height))
            return "File missing"
        return "N/A"

    @property
    def link_video(self):
        return self
        # return mark_safe('<img src="{}" width="{}" height="{}" />'.format(self.image.url, width, height))

    @property
    def play_button(self):
        if self.status == VideoStatus.NEW:
            if self.is_ready_for_task:
                return get_task_run(self.id)
            else:
                return mark_safe('<i class="fa-solid fa-circle-play" style="color: #a1a1a1;"></i> Water level missing')

        elif self.status == VideoStatus.QUEUE:
            return mark_safe(
                f"""<i class="fa-solid fa-stopwatch" style="color: #417893;"></i> Queued"""
            )
        elif self.status == VideoStatus.TASK:
            return mark_safe(
                f"""<i class="fa-solid fa-spinner fa-spin" style="color: #417893;"></i> Processing"""
            )
        elif self.status == VideoStatus.DONE:
            return mark_safe(
                f"""<img src="/static/admin/img/icon-yes.svg" alt="True"> Done"""
            )
        else:
            return mark_safe(
                f"""<img src="/static/admin/img/icon-no.svg" alt="True"> Error"""
            )

    @property
    def institute(self):
        return self.camera_config.institute

    class Meta:
        # organize tables along the camera config id and then per time stamp
        indexes = [models.Index(fields=['camera_config', 'timestamp'])]


    # TODO: Organize settings.py for choice local or S3.
    # TODO: when timestamp not provided, assume it must be harvested from the file time stamp
    # TODO: when task complete, status change to ERROR or FINISHED
