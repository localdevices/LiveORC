from rest_framework import serializers

from api.models import Video


class VideoSerializer(serializers.ModelSerializer):
    # camera_config = serializers.IntegerField(write_only=True, required=False)
    parent_lookup_kwargs = {
        # "site_pk": "camera_config__site__pk",
        "site_pk": "video_config__site__pk",
    }

    # def validate(self, attrs):
    #     video_config = attrs.get("video_config", None)
        # camera_config_id = attrs.pop("camera_config", None)

        # if video_config is None and camera_config_id is not None:
        #     video_config = VideoConfig.objects.filter(camera_config_id=camera_config_id).order_by("id").first()
        # if video_config is None:
        #     raise serializers.ValidationError("No VideoConfig exists for provided camera_config")
        # attrs["video_config"] = video_config

        # if attrs.get("video_config") is None:
        #     raise serializers.ValidationError("video_config is required")
        # return attrs

    class Meta:
        model = Video
        fields = "__all__"
        # fields = ['created_at', 'file', 'thumbnail', 'water_level', 'status', 'camera_config']

