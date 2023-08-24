from .models import Site, Profile, Recipe, CameraConfig, Video, Server, Task, Project, WaterLevel
from rest_framework import serializers


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Site
        fields = ['url', 'name', 'geom']


class CameraConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CameraConfig
        fields = ['url', 'name', 'site', 'start_date', 'end_date', 'version', 'camera_config']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['data']


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = ['data']


class VideoSerializer(serializers.HyperlinkedModelSerializer):
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


class WaterLevelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WaterLevel
        fields = "__all__"
