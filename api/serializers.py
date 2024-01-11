from .models import Site, Profile, Recipe, CameraConfig, Video, Server, Task, Project, TimeSeries
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

class InstituteOwned:
    requires_context = True

    def __call__(self, value, serializer_field):
        if "institute" in value:
            owned_institutes = [m.institute for m in serializer_field.context["request"].user.get_owned_institute_memberships()]
            if not (value["institute"] in owned_institutes):
                raise serializers.ValidationError(f'You do not own institute {value["institute"]}')

    # if value % 2 != 0:
    #     raise serializers.ValidationError('This field must be an even number.')

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"
        # fields = ['id', 'name', 'geom']
        validators = [InstituteOwned()]


class CameraConfigSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        "site_pk": "site_pk"
    }
    class Meta:
        model = CameraConfig
        fields = "__all__"

class CameraConfigCreateSerializer(CameraConfigSerializer):
    class Meta:
        model = CameraConfig
        exclude = ("site", )


class ProfileSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        "site_pk": "site_pk"
    }
    class Meta:
        model = Profile
        fields = "__all__"

class ProfileCreateSerializer(ProfileSerializer):
    class Meta:
        model = Profile
        exclude = ("site", )


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['name', 'data']
        validators = [InstituteOwned()]


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"
        # fields = ['created_at', 'file', 'thumbnail', 'water_level', 'status', 'camera_config']


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        fields = ['url', 'end_point', 'wildcard', 'username', 'frequency']
        validators = [InstituteOwned()]



class TaskSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        "site_pk": "site_pk",
        "video_pk": "video_pk",
    }

    class Meta:
        model = Task
        fields = "__all__"

class TaskCreateSerializer(TaskSerializer):
    class Meta:
        model = Task
        exclude = ("video",)


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        validators = [InstituteOwned()]


class TimeSeriesSerializer(serializers.ModelSerializer):
    # def create(self, validated_data):
    #     pass
    parent_lookup_kwargs = {
        "site_pk": "site_pk"
    }

    class Meta:
        model = TimeSeries
        fields = "__all__"

class TimeSeriesCreateSerializer(TimeSeriesSerializer):
    # parent_lookup_kwargs = {
    #     "site_pk": "site_pk"
    # }

    class Meta:
        model = TimeSeries
        exclude = ("site", )

