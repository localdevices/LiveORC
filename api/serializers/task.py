from rest_framework import serializers

from users.models import User
from api.models import Task
from api.custom_validators import institute_validator


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

