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
from django.conf import settings

from ..models import CameraConfig, Project, TimeSeries

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
    cap = cv2.VideoCapture(video_field.path)
    if frame_nr != 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_nr)
    res, image = cap.read()
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

class VideoStatus(models.IntegerChoices):
    NEW = 1, "New video"
    QUEUE = 2, "Send for processing"
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
        validators=[FileExtensionValidator(allowed_extensions=VIDEO_EXTENSIONS)]
    )
    keyframe = models.ImageField(
        upload_to=get_keyframe_path,
        help_text="Extracted frame for user contextual understanding or for making camera configurations",
        editable=False,
        max_length=254
    )
    thumbnail = models.ImageField(
        upload_to=get_thumb_path,
        help_text="Thumbnail frame for list views",
        editable=False
    )
    status = models.PositiveSmallIntegerField(
        choices=VideoStatus.choices,
        default=VideoStatus.NEW,
        editable=False,
        help_text="Status of processing"
    )
    camera_config = models.ForeignKey(CameraConfig, on_delete=models.CASCADE)
    time_series = models.ForeignKey(TimeSeries, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # move the file field to a separate variable temporaily.
        # This is in order to first get an ID on the video instance (otherwise video would be stored in a
        # folder called 'None'
        file = self.file
        self.file = None
        super(Video, self).save(*args, **kwargs)
        # now store the video
        self.file = file
        super(Video, self).save(*(), **{})
        if not(self.make_frames()):
            raise Exception('Could not create keyframe - is the file type valid?')
        super(Video, self).save(*(), **{})

    def make_frames(self):
        """
        make frame and thumbnail
        """
        add_frame_to_model(self.file, self.keyframe)
        add_frame_to_model(self.file, self.thumbnail, suffix="_thumb", thumb=True)
        return True

    def make_thumbnail(self):

        raise NotImplementedError

    @property
    def thumbnail_preview(self):
        height = int(settings.THUMBSIZE)
        width = int((self.thumbnail.width / self.thumbnail.height) * height)
        if self.thumbnail:
            return mark_safe('<img src="{}" width="{}" height="{}" />'.format(self.thumbnail.url, width, height))
        return ""

    @property
    def video_preview(self):
        height = int(300)
        width = int((self.keyframe.width / self.keyframe.height) * height)
        uri = reverse('video-playback', args=(str(self.id)))
        mimetype, _ = mimetypes.guess_type(self.file.name)

        if self.file:
            return mark_safe(
                '<video src="{}" width="{}" height="{}" type={} controls preload="none"/>'.format(
                    uri,
                    # self.file.url,
                    width,
                    height,
                    mimetype
                )
            )
        return ""


    class Meta:
        # organize tables along the camera config id and then per time stamp
        indexes = [models.Index(fields=['camera_config', 'timestamp'])]


    # TODO: Organize settings.py for choice local or S3.
    # TODO: when timestamp not provided, assume it must be harvested from the file time stamp
    # TODO: when water level provided, change status and start a task
    # TODO: when task complete, status change to ERROR or FINISHED
