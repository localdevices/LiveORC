from django.db import models


class ServerType(models.IntegerChoices):
    FTP = 1, "FTP"
    ODK = 2, "ODK Collect"
    # ("SFTP", "SFTP")


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

