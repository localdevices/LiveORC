from rest_framework import serializers

from users.models import User
from api.models import CameraConfig
from api.custom_validators import institute_validator

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

