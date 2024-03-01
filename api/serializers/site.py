from rest_framework import serializers

from api.models import Site
from api.custom_validators import institute_validator


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"

    def validate(self, data):
        institute_validator(institute=data.get("institute"), user=self.context["request"].user)
        return data
