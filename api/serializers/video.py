from rest_framework import serializers

from api.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"
        # fields = ['created_at', 'file', 'thumbnail', 'water_level', 'status', 'camera_config']

