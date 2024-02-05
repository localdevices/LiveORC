from drf_queryfields import QueryFieldsMixin
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from users.models import User
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from .models import Site, Profile, Recipe, CameraConfig, Video, Server, Task, Project, TimeSeries, Device

def institute_validator(institute, user):
    # if institute is not None
    if institute:
        owned_institutes = [m.institute for m in user.get_owned_institute_memberships()]
        if not (institute in owned_institutes):
            raise PermissionDenied()
    return


class InstituteOwned:
    requires_context = True

    def __call__(self, value, serializer_field):
        if "institute" in value:
            owned_institutes = [m.institute for m in serializer_field.context["request"].user.get_owned_institute_memberships()]
            if not (value["institute"] in owned_institutes):
                raise serializers.ValidationError(f'You do not own institute {value["institute"]}')

class SiteOwned:
    requires_context = True

    def __call__(self, value, serializer_field):
        if "site" in value:
            user = User.objects.get(pk=serializer_field.initial_data["creator"])
            owned_institutes = [m.institute for m in user.get_owned_institute_memberships()]
            if not (value["site"].institute in owned_institutes):
                raise serializers.ValidationError(f'You do not own institute {value["site"].institute}')


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
        validators = [InstituteOwned()]



class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"

    def validate(self, data):
        institute_validator(institute=data.get("institute"), user=self.context["request"].user)
        return data

class CameraConfigSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        "site_pk": "site_pk"
    }
    class Meta:
        model = CameraConfig
        fields = "__all__"

    def validate(self, data):
        user = User.objects.get(pk=self.initial_data["creator"])
        institute_validator(institute=data.get("site").institute, user=user)
        return data


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
        fields = ['name', 'data', "institute"]
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

    def validate(self, data):
        user = User.objects.get(pk=self.initial_data["creator"])
        institute_validator(institute=data.get("video").institute, user=user)
        return data


class TaskCreateSerializer(TaskSerializer):
    class Meta:
        model = Task
        exclude = ("video",)


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        validators = [InstituteOwned()]


class TimeSeriesSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    # def create(self, validated_data):
    #     pass
    parent_lookup_kwargs = {
        "site_pk": "site_pk"
    }

    class Meta:
        model = TimeSeries
        fields = [
            "id",
            "timestamp",
            "h",
            "q_05",
            "q_25",
            "q_50",
            "q_75",
            "q_95",
            "wetted_surface",
            "wetted_perimeter",
            "fraction_velocimetry",
            "creator",
            "site",
            "video"
        ]
        read_only_fields = ("video", )

    def validate(self, data):
        user = User.objects.get(pk=self.initial_data["creator"])
        institute_validator(institute=data.get("site").institute, user=user)
        return data

class TimeSeriesCreateSerializer(TimeSeriesSerializer):
    # parent_lookup_kwargs = {
    #     "site_pk": "site_pk"
    # }

    class Meta:
        model = TimeSeries
        exclude = ("site", )

