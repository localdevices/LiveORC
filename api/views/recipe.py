from rest_framework import viewsets, permissions
from LiveORC.utils.api.viewsets import InstitutionMixin
from api.serializers import RecipeSerializer
from api.models import Recipe

class RecipeViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows recipes to be viewed or edited.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "patch"]

