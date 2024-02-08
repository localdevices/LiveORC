from rest_framework import serializers

from api.models import Profile


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
