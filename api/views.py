from rest_framework import viewsets, permissions
from .models import Site
from .serializers import SiteSerializer



class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows sites to be viewed or edited.
    """
    queryset = Site.objects.all().order_by('name')
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]

# Create your views here.
