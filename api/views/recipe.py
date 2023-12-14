from rest_framework import permissions
from api.serializers import RecipeSerializer
from api.models import Recipe
from api.views import BaseModelViewSet
from django_filters.rest_framework import DjangoFilterBackend


class RecipeViewSet(BaseModelViewSet):
    """
    API endpoints that allows recipes to be viewed or edited.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "patch"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['institute']

    def get_queryset(self):
        """
        Optionally restricts the returned recipes to a given institute,
        by filtering against an `institute` query parameter in the URL.
        """
        queryset = Recipe.objects.all()
        institute = self.request.query_params.get('institute', None)
        if self.request.user.is_superuser:
            return queryset
        if institute:
            queryset = queryset.filter(institute=institute)
        return queryset.none()

