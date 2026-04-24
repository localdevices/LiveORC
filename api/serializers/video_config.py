from rest_framework import serializers
from users.models import User
from api.custom_validators import institute_validator
from api.models import VideoConfig


class VideoConfigSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        # "site_pk": "camera_config__site__pk",
        "site_pk": "site_pk",
    }

    class Meta:
        model = VideoConfig
        fields = "__all__"

    def validate(self, attrs):
        creator_pk = self.initial_data.get("creator") if hasattr(self, "initial_data") else None
        if creator_pk:
            user = User.objects.get(pk=creator_pk)
        else:
            user = self.context["request"].user

        # user = attrs.get("creator")
        if user is None and self.instance is not None:
            user = self.instance.creator
        if user is None:
            user = self.context["request"].user
            
        site = attrs.get("site")
        # validate if site is compliant with user permissions
        institute_validator(institute=site.institute, user=user)

        camera_config = attrs.get("camera_config")
        if camera_config and site and camera_config.site_id != site.id:
            raise serializers.ValidationError("camera config must belong to the same site as video config")
        # if camera_config:
        #     institute_validator(institute=camera_config.site.institute, user=user)

        cross_section = attrs.get("cross_section")
        if cross_section and site and cross_section.site_id != site.id:
            raise serializers.ValidationError("cross_section must belong to the same site as video config")

        cross_section_wl = attrs.get("cross_section_wl")
        if cross_section_wl and site and cross_section_wl.site_id != site.id:
            raise serializers.ValidationError("cross_section_wl must belong to the same site as video config")

        return attrs


class VideoConfigCreateSerializer(VideoConfigSerializer):
    class Meta: # (VideoConfigSerializer.Meta):
        model = VideoConfig
        exclude = ("site",)


class VideoConfigUpdateSerializer(VideoConfigSerializer):
    class Meta: # (VideoConfigSerializer.Meta):
        model = VideoConfig
        exclude = ("creator",)

    def validate(self, attrs):
        return super().validate(attrs)
