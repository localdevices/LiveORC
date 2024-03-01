from rest_framework import serializers

from users.models import User
from api.models import TaskForm
from api.custom_validators import institute_validator


class TaskFormSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        "device_pk": "site_pk",
    }

    class Meta:
        model = TaskForm
        fields = "__all__"

    def validate(self, data):
        user = User.objects.get(pk=self.initial_data["creator"])
        institute_validator(institute=data.get("device").institute, user=user)
        return data

