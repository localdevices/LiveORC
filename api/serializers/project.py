from rest_framework import serializers

from api.models import Project
from api.custom_validators import InstituteOwned


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        validators = [InstituteOwned()]

