import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.gis.db import models as gismodels


from django.core.exceptions import ValidationError
import pyorc

class ServerType(models.IntegerChoices):
    FTP = 1, "FTP"
    ODK = 2, "ODK Collect"
    # ("SFTP", "SFTP")

class VideoStatus(models.IntegerChoices):
    NEW = 1, "New video"
    QUEUE = 2, "Send for processing"
    TASK = 3, "Being processed"
    DONE = 4, "Finished"
    ERROR = 5, "Error occurred"

class TaskAction(models.IntegerChoices):
    CANCEL = 1, "Cancel"
    REMOVE = 2, "Remove"
    RESTART = 3, "Restart"

class Site(gismodels.Model):
    """
    Location of one or more videos
    """
    def __str__(self):
        return "{:s} at lon: {:0.1f}, lat: {:0.1f}".format(self.name, self.geom.x, self.geom.y)

    name = models.CharField(max_length=100, help_text="Recognizable unique name for your site")
    # x = models.FloatField("x-coordinate", help_text="If a CRS is provided, the x-coordinate must be provided in this CRS, otherwise defaults to WGS84 latitude longitude")
    # y = models.FloatField("y-coordinate", help_text="If a CRS is provided, the y-coordinate must be provided in this CRS, otherwise defaults to WGS84 latitude longitude")
    # crs = models.CharField("Coordinate Reference System", max_length=254, default="EPSG:4326", help_text='You may provide a CRS in e.g. EPSG code format (e.g. "EPSG:4326", well-known text formats or proj4 string.')
    geom = gismodels.PointField("Location", srid=4326, help_text="Approximate location of the site")

## UNCOMMENT MODELS BELOW AS THEY ARE BEING DEVELOPED
#
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

    # TODO also connect to server
    # TODO connect to recipe and profile (where necessary)

    def clean(self):
        super().clean()
        try:
            pyorc.CameraConfig(**self.data)
            # see if you can make a camera config object
        except BaseException as e:
            raise ValidationError(f"Problem with Camera Configuration: {e}")

class Profile(models.Model):
    """
    Contains the river profile as a geojson
    """
    data = models.JSONField(help_text="GeoJSON fields containing Point (x,y,z) geometries that encompass a cross section")
    camera_config = models.ForeignKey(CameraConfig, on_delete=models.CASCADE, blank=True, null=True)
    # TODO: change into a GeoJSON field (using GeoDjango)

    def clean(self):
        super().clean()
        try:
            pyorc.CameraConfig(**self.data)
            # see if you can make a camera config object
        except BaseException as e:
            raise ValidationError(f"Problem with Camera Configuration: {e}")

class Recipe(models.Model):
    """
    Contains settings to process videos
    """
    data = models.JSONField(help_text="JSON formatted recipe for processing videos. See https://localdevices.github.io/pyorc/user-guide/cli.html")
    version = models.CharField(max_length=15, blank=True, default=pyorc.__version__, editable=False)

    def clean(self):
        super().clean()
        # data = json.loads(json.dumps(self.data))
        # print(data)
        # json_object = json.dumps(data, indent=4)
        # with open("recipe.json", "w") as f:
        #     f.write(json_object)
        try:
            pyorc.cli.cli_utils.validate_recipe(self.data)
        except BaseException as e:
            raise ValidationError(f"Problem with recipe: {e}")

class Project(models.Model):
    """
    Project that holds together one or several videos at different sites (for surveys)
    """
    name = models.CharField(max_length=100, help_text="Name of project")
    description = models.TextField(
        help_text="Summary of the project details, e.g. sites, client, purpose, intended outcome"
    )


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
        blank=True,
        help_text="Data and time on which video was taken. If not provided by the user, this is taken from the file's time stamp"
    )
    file = models.FileField()
    keyframe = models.ImageField(help_text="Extracted frame for user contextual understanding or for making camera configurations")
    thumbnail = models.ImageField(help_text="Thumbnail frame for list views")
    water_level = models.FloatField(blank=True, null=True, help_text="Water level occurring within time range close to timestamp of video")
    status = models.PositiveSmallIntegerField(
        choices=VideoStatus.choices,
        default=VideoStatus.NEW,
        editable=False,
        help_text="Status of processing"
    )
    camera_config = models.ForeignKey(CameraConfig, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO: setup storage model for S3. Organize settings.py for choice local or S3.
    # TODO: when timestamp not provided, assume it must be harvested from the file time stamp
    # TODO: when water level provided, change status and start a task
    # TODO: when task complete, status change to ERROR or FINISHED
class Server(models.Model):
    """
    Server configuration with specific end points and
    file wildcards for frequent retrieval of videos
    """
    type = models.PositiveSmallIntegerField(
        choices=ServerType.choices,
        default=ServerType.FTP
    )
    url = models.URLField(max_length=254, help_text="URL of server including port number, in the form of <your-protocol>://<your-server-name>:<your-port-nr> e.g. ftp://liveopenrivercam.com:2345")
    end_point = models.CharField(max_length=254, help_text='End point of server, where files are stored, e.g. "videos" would result in scraping from <your-protocol>://<your-server-name>:<your-port-nr>/videos')
    wildcard = models.CharField(max_length=100, default="*", help_text="Wildcard to use to look for (new) files")
    token = models.CharField(max_length=254, help_text="Access token to site", blank=True, null=True)
    username = models.CharField(max_length=100, help_text="Your user name", blank=True, null=True)
    password = models.CharField(max_length=100, help_text="Your password", blank=True, null=True)
    frequency = models.DurationField(help_text="Amount of seconds")  # TODO maybe this needs to go to the cameraconfig.


class Task(models.Model):
    """
    Task run on video
    """
    uuid = models.CharField(max_length=255, default='', blank=True, help_text="Identifier of task as stored by RabbitMQ messaging service")
    pending_action = models.PositiveSmallIntegerField(choices=TaskAction.choices)
    asset_paths = models.JSONField(default=dict)  # TODO: assets should be filled using task callbacks with new entries such as asset_paths["piv"] = <relative_path_to_piv>
    public = models.BooleanField(default=False)  # very cool to make permalinks publically available when a user wants.
    progress = models.FloatField(default=0., help_text="Value between 0 and 1 indicating the progress of the task", blank=True)

    video = models.ForeignKey(Video, on_delete=models.CASCADE)


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
