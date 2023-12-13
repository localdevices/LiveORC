from api.serializers import SiteSerializer
from api.models import Site
from api.views import BaseModelViewSet
from django_filters.rest_framework import DjangoFilterBackend


class SiteViewSet(BaseModelViewSet):

    """
    API endpoints that allows sites to be viewed or edited.
    """
    queryset = Site.objects.all().order_by('name')
    serializer_class = SiteSerializer

    http_method_names = ["post", "get", "patch", "delete"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['institute']

    def get_queryset(self):
        """
        Optionally restricts the returned sites to a given institute,
        by filtering against an `institute` query parameter in the URL.
        """
        queryset = Site.objects.all()
        institute = self.request.query_params.get('institute', None)
        if self.request.user.is_superuser:
            return queryset
        if institute:
            queryset = queryset.filter(institute=institute)
        return queryset.none()


