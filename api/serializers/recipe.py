from rest_framework import serializers

from api.models import Recipe
from api.custom_validators import InstituteOwned


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['name', 'data', "institute"]
        validators = [InstituteOwned()]

