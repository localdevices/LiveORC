from rest_framework import serializers

from api.models import CrossSection


class CrossSectionSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        "site_pk": "site_pk"
    }

    class Meta:
        model = CrossSection
        fields = "__all__"


class CrossSectionCreateSerializer(CrossSectionSerializer):
    class Meta:
        model = CrossSection
        exclude = ("site", )

