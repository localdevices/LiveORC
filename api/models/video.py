import io
import mimetypes
import os
import urllib
import zipfile

import cv2
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import storage
from django.core.files.storage import FileSystemStorage, storages
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import mark_safe
from django.core.files.base import ContentFile
import numpy as np
from PIL import Image

from .project import Project
from .time_series import TimeSeries
from .video_config import VideoConfig


VIDEO_EXTENSIONS = ["MOV", "MKV", "MP4", "AVI", "M4V"]

class OverwriteFileSystemStorage(FileSystemStorage):
    """Custom FileSystemStorage that overwrites existing files with the same name."""
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name


def select_storage():
    storage = storages["media"]
    if "FileSystemStorage" in str(type(storage)):
        # override save behaviour, make sure files are overwritten when a new video with the same name is uploaded
        return OverwriteFileSystemStorage(location=storage.location, base_url=storage.base_url)
    # for S3 storage, the overwrite behaviour is already set in the settings, so we can just return the storage as is
    return storage


def storage_path(file_field):
    if "FileSystemStorage" in str(file_field.storage):
        # local storage used
        return file_field.path
    else:
        # remote storage used
        return file_field.url


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
    if "ImageFieldFile" in repr(video_field):
        if "://" in storage_path(video_field):
            # url requires an explicit opening of the url
            img = Image.open(
                urllib.request.urlopen(
                    storage_path(video_field)
                )
            )
        else:
            img = Image.open(storage_path(video_field))
    elif "FieldFile" in repr(video_field):
        # a video is passed, so use opencv to get the key frame
        cap = cv2.VideoCapture(storage_path(video_field))
        if frame_nr != 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_nr)
        res, image = cap.read()
        # turn into RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # turn into PIL object
        img = Image.fromarray(image, "RGB")
    img_name, video_extension = os.path.splitext(os.path.basename(video_field.name))
    img_extension = ".jpg"
    FTYPE = 'JPEG'
    img_filename = img_name + suffix + img_extension
    # Save thumbnail to in-memory file as StringIO
    if thumb:
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
    if not instance.video_config:
        raise ValueError("video_config with camera_config is required before storing video files")
    end_point = os.path.join(
        "videos",
        str(instance.video_config.site.id),
        instance.timestamp.strftime("%Y%m%d"),
        instance.timestamp.strftime("%Y%m%dT%H%M%S") + ext
    )
    return end_point


def get_thumb_path(instance, filename):
    if not instance.video_config:
        raise ValueError("video_config with camera_config is required before storing thumbnails")
    end_point = os.path.join(
        "thumb",
        str(instance.video_config.site.id),
        instance.timestamp.strftime("%Y%m%d"),
        filename
    )
    return end_point


def get_keyframe_path(instance, filename):
    if not instance.video_config:
        raise ValueError("video_config with camera_config is required before storing keyframes")
    end_point = os.path.join(
        "keyframe",
        str(instance.video_config.site.id),
        instance.timestamp.strftime("%Y%m%d"),
        filename
    )
    return end_point


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
        storage=select_storage
    )
    keyframe = models.ImageField(
        upload_to=get_keyframe_path,
        help_text="Extracted frame for user contextual understanding or for making camera configurations",
        editable=False,
        max_length=254,
        storage=select_storage
    )
    image = models.ImageField(
        upload_to=get_video_path,
        help_text="Image showing the results of a velocimetry analysis",
        null=True,
        storage=select_storage
    )
    thumbnail = models.ImageField(
        upload_to=get_thumb_path,
        help_text="Thumbnail frame for list views",
        editable=False,
        storage=select_storage
    )
    status = models.PositiveSmallIntegerField(
        choices=VideoStatus.choices,
        default=VideoStatus.NEW,
        # editable=False,
        help_text="Status of processing"
    )
    video_config = models.ForeignKey(VideoConfig, on_delete=models.SET_NULL, null=True, blank=True)
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
                super(Video, self).save(*(), **{})
                return
            # look for time series instances that are for the same site and not yet associated with a video
            if not self.video_config:
                super(Video, self).save(*(), **{})
                return
            ts_at_site = TimeSeries.objects.filter(
                site = self.video_config.site
            ) # TODO: exclude time series records that are already used by another video ....filter(
            #     video__time_series__ne=...
            if len(ts_at_site) != 0:
                # apparently there is a candidate time series record
                ts_closest = get_closest_to_dt(ts_at_site, self.timestamp)
                # check if time diff is acceptable
                dt = np.abs(self.timestamp - ts_closest.timestamp)
                if dt < self.video_config.camera_config.allowed_dt:
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
        elif self.image:
            # only add a thumbnail in this case
            add_frame_to_model(self.image, self.thumbnail, suffix="_thumb", thumb=True)
        else:
            # do nothing, no video file or image are provided
            pass
        return True

    def make_thumbnail(self):

        raise NotImplementedError


    # @property
    # def effective_camera_config(self):
    #     return self.video_config.camera_config if self.video_config else None

    # @property
    # def effective_video_config(self):
    #     return self.video_config if self.video_config else None

    def save_result_file(self, fn, file_content):
        """
        Save a result file to the appropriate storage.
        
        Parameters
        ----------
        fn : str
            Result file name (e.g., "2d.nc", "2d_mask.nc", "1d.nc", "2d_ugrid.nc", "orc.log")
        file_content : bytes or file-like object
            Content to save
        
        Returns
        -------
        str
            Path/URL of saved file (local path or S3 URL)
        """
        
        # Generate the file path
        file_path = os.path.join(
            "results",
            str(self.video_config.site.id),
            self.timestamp.strftime("%Y%m%d"),
            str(self.id),
            fn
        )
        
        # Save using the appropriate storage
        storage = select_storage()
        storage.save(file_path, ContentFile(file_content))
        return file_path

    def get_log_file(self):
        """
        Retrieve the log file content for this video.
        
        Returns
        -------
        str or None
            Content of the log file, or None if not found
        """
        log_file_path = os.path.join(
            "results",
            str(self.video_config.site.id),
            self.timestamp.strftime("%Y%m%d"),
            str(self.id),
            "orc.log"
        )
        storage = select_storage()
        if storage.exists(log_file_path):
            with storage.open(log_file_path, 'r') as f:
                return f.read()
        return None

    def get_result_file(self, key):
        """
        Retrieve a result file path/URL from storage.
        
        Parameters
        ----------
        key : str
            Result file key (e.g., "2d", "2d_mask")
        
        Returns
        -------
        str or None
            relative path of file within selected storage, None if file doesn't exist
        """
        file_path = os.path.join(
            "results",
            str(self.video_config.site.id),
            self.timestamp.strftime("%Y%m%d"),
            str(self.id),
            f"{key}.nc"
        )
        
        storage = select_storage()
        if storage.exists(file_path):
            return file_path
        return None


    def delete_result_file(self, key):
        """
        Delete a result file from storage.
        """
        file_path = os.path.join(
            "results",
            str(self.video_config.site.id),
            self.timestamp.strftime("%Y%m%d"),
            str(self.id),
            f"{key}.nc"
        )
        storage = select_storage()
        if storage.exists(file_path):
            storage.delete(file_path)


    def download_result(self, key):
        """
        Download a result file from storage.
        
        Parameters
        ----------
        key : str
            Result file key (e.g., "2d", "2d_mask")
        
        Returns
        -------
        HttpResponse
            Response containing the file for download, or 404 if not found
        """
        file_path = self.get_result_file(key)
        if not file_path:
            return HttpResponse(
                f"No result file found for {key} for video {self.id} at site {self.video_config.site.name}.",
                status=404
            )
        storage = storages["media"]
        with storage.open(file_path, 'rb') as f:
            bin_data = f.read()
        # Determine the filename for download
        netcdf_fn = f"{self.video_config.site.name}_{self.video_config.name}_{key}.nc"
        response = HttpResponse(bin_data, content_type='application/x-netcdf')
        response['Content-Disposition'] = f'attachment; filename="{netcdf_fn}"'
        return response


    def download_all_results(self):
        """
        Create a zip file containing all result files for this video.
        
        Returns
        -------
        bytes or None
            Content of the zip file, or None if no results exist
        """
    
        if self.id is None or not (self.video_config and self.video_config.site):
            return None
        
        results_base = os.path.join(
            "results",
            str(self.video_config.site.id),
            self.timestamp.strftime("%Y%m%d"),
            str(self.id)
        )
        
        storage = select_storage()
        
        try:
            _, files = storage.listdir(results_base)
        except (FileNotFoundError, OSError):
            # Results directory doesn't exist
            return None
        
        if not files:
            return None
        
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_name in files:
                file_path = os.path.join(results_base, file_name)
                with storage.open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Add to zip with just the filename (not full path)
                zip_file.writestr(file_name, file_content)
        
        zip_buffer.seek(0)

        # zip_buffer.getvalue()
        # Determine the filename for download
        zip_fn = f"{self.video_config.site.name}_{self.video_config.name}.zip"
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_fn}"'
        return response


    @property
    def results_path(self):
        # construct path from the video id and timestamp. The structure should be:
        # results/<site_id>/<YYYYMMDD>/<video_id>/
        if self.id is None:
            return None

        if self.video_config and self.video_config.site:
            return os.path.join(
                "results",
                str(self.video_config.site.id),
                self.timestamp.strftime("%Y%m%d"),
                str(self.id)
            )
        else:
            return None


    @property
    def thumbnail_preview(self):
        if self.thumbnail:
            height = int(settings.THUMBSIZE) / 2
            try:
                width = int((self.thumbnail.width / self.thumbnail.height) * height)
            except:
                return mark_safe("File missing")
                # width = height * 1.5
            if not self.video_config:
                return mark_safe("N/A")
            uri = reverse('api:site-video-thumbnail', args=([str(self.video_config.site.id), str(self.id)]))
            return mark_safe('<img src="{}" width="{}" height="{}" />'.format(uri, width, height))
        return mark_safe("N/A")

    @property
    def is_ready_for_task(self):
        if not self.time_series:
            return False
        if not self.video_config:
            return False
        video_config = self.video_config
        if not video_config:
            return False
        if not (video_config.recipe and video_config.cross_section):
            return False

        return (self.status == VideoStatus.NEW or self.status == VideoStatus.ERROR) and self.time_series.h is not None

    @property
    def video_preview(self):
        try:
            if not self.video_config:
                return "video config missing"
            height = int(300)
            width = int((self.keyframe.width / self.keyframe.height) * height)
            uri = reverse('api:site-video-playback', args=([str(self.video_config.site.id), str(self.id)]))
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
        except:
            return "video media not available"
        return ""

    @property
    def image_preview(self):
        height = int(300)
        if self.image:
            try:
                if not self.video_config:
                    return mark_safe("video config missing")
                width = int((self.image.width / self.image.height) * height)
                uri = reverse('api:site-video-image', args=([str(self.video_config.site.id), str(self.id)]))
                return mark_safe('<img src="{}" width="{}" height="{}" />'.format(uri, width, height))
            except:
                return mark_safe("File missing")
        return mark_safe("N/A")

    @property
    def link_video(self):
        return self
        # return mark_safe('<img src="{}" width="{}" height="{}" />'.format(self.image.url, width, height))



        # elif not obj.time_series:
        #     messages.error(request, f"Video {obj.id} does not yet have a water level at associated time stamp. ")
        # elif not obj.camera_config.profile:
        #     messages.error(request, f"Video {obj.id}'s camera configuration does not have a profile. Add a profile to the camera configuration. ")
        # elif not obj.camera_config.recipe:
        #     messages.error(request,f"Video {obj.id}'s camera configuration does not have a recipe. Add a recipe to the camera configuration. ")
        # elif obj.status == VideoStatus.QUEUE or obj.status == VideoStatus.TASK:
        #     messages.error(request, f"Video {obj.id} is already queued or being processed. ")


    @property
    def play_button(self):
        if self.status == VideoStatus.NEW:
            if self.is_ready_for_task:
                return get_task_run(self.id)
            else:
                if not self.time_series:
                    queue_msg = "water level missing"
                elif not self.video_config or not self.video_config.cross_section:
                    queue_msg = "no cross section"
                elif not self.video_config.recipe:
                    queue_msg = "no recipe"
                else:
                    queue_msg = "n/a"
                return mark_safe(f'<i class="fa-solid fa-circle-play" style="color: #a1a1a1;"></i> {queue_msg} ')

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
        if self.video_config and self.video_config.site:
            return self.video_config.site.institute
        return None

    def create_task(self, request, *args, **kwargs):
        from api.models import Task
        from api.task_utils import get_task
        from api.tasks import run_nodeorc

        # launch creation of a new task
        task_body = get_task(self, request, serialize=False, *args, **kwargs)
        # send over validated task to worker
        job = run_nodeorc.delay(self.pk, task_body)
        task = {
            "id": task_body["id"],
            "broker_id": job.id,
            "task_body": task_body,
            "video": self,
            "creator": request.user
        }
        # validation
        Task.objects.create(**task)

        # once the task is set, change the status of the video
        self.status = VideoStatus.QUEUE
        self.save()


    class Meta:
        # organize tables along the video config id and then per time stamp
        indexes = [models.Index(fields=['video_config', 'timestamp'])]


@receiver(pre_delete, sender=Video)
def delete_video_files(sender, instance, **kwargs):
    """
    Signal handler to delete all associated files when a Video is deleted.
    Deletes: file, keyframe, thumbnail, image, and all result files.
    """
    storage = select_storage()
    
    # Delete model file fields
    for field_name in ['file', 'keyframe', 'thumbnail', 'image']:
        field_file = getattr(instance, field_name, None)
        if field_file and field_file.name:
            try:
                storage.delete(field_file.name)
            except Exception as e:
                print(f"Error deleting {field_name}: {str(e)}")
    
    # Delete all result files in the results directory
    if instance.id and instance.video_config and instance.video_config.site:
        results_base = os.path.join(
            "results",
            str(instance.video_config.site.id),
            instance.timestamp.strftime("%Y%m%d"),
            str(instance.id)
        )
        try:
            _, files = storage.listdir(results_base)
            for file_name in files:
                file_path = os.path.join(results_base, file_name)
                try:
                    storage.delete(file_path)
                except Exception as e:
                    print(f"Error deleting result file {file_name}: {str(e)}")
            # also remove the results directory once empty
            try:
                storage.delete(results_base)
            except Exception as e:
                print(f"Error deleting results directory: {str(e)}")
        except (FileNotFoundError, OSError):
            # Results directory doesn't exist, nothing to clean up
            pass