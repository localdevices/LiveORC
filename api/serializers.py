from .models import Site, Profile, Recipe, CameraConfig, Video, Server, Task, Project, TimeSeries
from rest_framework import serializers


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Site
        # fields = "__all__"
        fields = ['id', 'name']# , 'geom']


class CameraConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraConfig
        fields = "__all__"
        # fields = ['url', 'name', 'site', 'start_date', 'end_date', 'camera_config']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['data']


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = ['data']


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"
        # fields = ['created_at', 'file', 'thumbnail', 'water_level', 'status', 'camera_config']


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        fields = ['url', 'end_point', 'wildcard', 'username', 'frequency']



class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class TimeSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSeries
        fields = "__all__"
