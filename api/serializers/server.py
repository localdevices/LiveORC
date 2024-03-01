from rest_framework import serializers

from api.models import Server
from api.custom_validators import InstituteOwned


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        fields = ['url', 'end_point', 'wildcard', 'username', 'frequency']
        validators = [InstituteOwned()]

