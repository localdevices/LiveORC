from rest_framework import viewsets, permissions
from .models import Site, Profile, Recipe, CameraConfig
from .serializers import SiteSerializer, ProfileSerializer, RecipeSerializer, CameraConfigSerializer


class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows sites to be viewed or edited.
    """
    queryset = Site.objects.all().order_by('name')
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]



class CameraConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows camera configurations to be viewed or edited.
    """
    queryset = CameraConfig.objects.all().order_by('name')
    serializer_class = CameraConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class RecipeViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows recipes to be viewed or edited.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

# Create your views here.
