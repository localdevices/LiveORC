from rest_framework import permissions
from api.serializers import RecipeSerializer
from api.models import Recipe
from api.views import BaseModelViewSet


class RecipeViewSet(BaseModelViewSet):
    """
    API endpoints that allows recipes to be viewed or edited.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "patch"]

