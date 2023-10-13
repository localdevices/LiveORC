from api.serializers import SiteSerializer
from api.models import Site
from api.views import BaseModelViewSet

class SiteViewSet(BaseModelViewSet):

    """
    API endpoints that allows sites to be viewed or edited.
    """
    queryset = Site.objects.all().order_by('name')
    serializer_class = SiteSerializer

    http_method_names = ["post", "get", "patch", "delete"]
