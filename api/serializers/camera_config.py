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
        creator_pk = self.initial_data.get("creator") if hasattr(self, "initial_data") else None
        if creator_pk:
            user = User.objects.get(pk=creator_pk)
        else:
            user = self.context["request"].user
        institute_validator(institute=data.get("site").institute, user=user)
        return data


class CameraConfigCreateSerializer(CameraConfigSerializer):
    class Meta:
        model = CameraConfig
        exclude = ("site",)


class CameraConfigUpdateSerializer(CameraConfigSerializer):
    class Meta:
        model = CameraConfig
        exclude = ("site", "creator")

    def validate(self, data):
        """Pass on the attributes as is, without user / creator / site check."""
        return data
