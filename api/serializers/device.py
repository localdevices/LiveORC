from rest_framework import serializers

from api.models import Device
from api.custom_validators import InstituteOwned

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
        validators = [InstituteOwned()]
