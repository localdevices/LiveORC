from drf_queryfields import QueryFieldsMixin
from rest_framework import serializers

from users.models import User

from api.models import TimeSeries
from api.custom_validators import institute_validator


class TimeSeriesSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    # def create(self, validated_data):
    #     pass
    parent_lookup_kwargs = {
        "site_pk": "site_pk"
    }

    class Meta:
        model = TimeSeries
        fields = [
            "id",
            "timestamp",
            "h",
            "q_05",
            "q_25",
            "q_50",
            "q_75",
            "q_95",
            "wetted_surface",
            "wetted_perimeter",
            "fraction_velocimetry",
            "creator",
            "site",
            "video"
        ]
        read_only_fields = ("video", )

    def validate(self, data):
        user = User.objects.get(pk=self.initial_data["creator"])
        institute_validator(institute=data.get("site").institute, user=user)
        return data

class TimeSeriesCreateSerializer(TimeSeriesSerializer):
    # parent_lookup_kwargs = {
    #     "site_pk": "site_pk"
    # }

    class Meta:
        model = TimeSeries
        exclude = ("site", )

