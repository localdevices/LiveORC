import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin


# class CameraConfig(models.Model):
#     raise NotImplementedError

class Site(models.Model):
    """
    Location of one or more videos
    """
    def __str__(self):
        return f"{self.name}"

    name = models.CharField(max_length=100)
    x = models.FloatField("x-coordinate")
    y = models.FloatField("y-coordinate")
    crs = models.CharField("Coordinate Reference System", max_length=254, default="EPSG:4326")

#
# class Profile(models.Model):
#     """
#     Contains the river profile as a geojson
#     """
#     raise NotImplementedError
#
# class Recipe(models.Model):
#     """
#     Contains settings to process videos
#     """
#     raise NotImplementedError
#
# class Video(models.Model):
#     """
#     Video object with water level and flow information
#     """
#     raise NotImplementedError
#
# class Server(models.Model):
#     """
#     Server for frequent retrieval of videos
#     """
#     raise NotImplementedError
#
# class Task(models.Model):
#     """
#     Task run on video
#     """
#     raise NotImplementedError
#
# class Project(models.Model):
#     """
#     Project that holds together one or several videos at different sites (for surveys)
#     """
#     raise NotImplementedError
#
# class WaterLevel(models.Model):
#     """
#     temporary water level for sites used to provide water levels to uploaded videos
#     """
#     raise NotImplementedError
#
#
