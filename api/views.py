from django.http import HttpResponse, request
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework import renderers
from typing import Optional
from .models import Site, Profile, Recipe, CameraConfig, Video, TimeSeries, Task
from .serializers import SiteSerializer, ProfileSerializer, RecipeSerializer, CameraConfigSerializer, VideoSerializer, TimeSeriesSerializer, TaskSerializer
import mimetypes


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


class TimeSeriesViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows recipes to be viewed or edited.
    """
    queryset = TimeSeries.objects.all()
    serializer_class = TimeSeriesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # video can also be retrieved nested per site, by filtering on the site of the cameraconfig property.
        return TimeSeries.objects.filter(site=self.kwargs['site_pk'])

class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows recipes to be viewed or edited.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]



class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows recipes to be viewed or edited.
    """
    # lookup_field = "camera_config__site"
    queryset = Video.objects.all().order_by('-timestamp')
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # video can also be retrieved nested per site, by filtering on the site of the cameraconfig property.
        return Video.objects.filter(camera_config__site__id=self.kwargs['site_pk'])

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def playback(self, request, *args, **kwargs):
        video = self.get_object().file
        mimetype, _ = mimetypes.guess_type(video.file.name)
        return HttpResponse(video, content_type=mimetype)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def create_task(self, request, *args, **kwargs):
        instance = self.get_object()
        task = instance.make_task()
        # print(f"URL: {request.build_absolute_uri(reverse('video'))}")
        return redirect('api:video-list')



# class VideoSiteViewSet(VideoViewSet):
#     queryset = Video.objects.all()
#     def get_queryset(self):
#         site: Optional[int] = self.request.query_params.get("site", None)
#         if site is not None:
#             return Video.objects.filter(site=site)
#         return super().get_queryset()
#

# @api_view(["GET"])
# def get_video(request, id):
#     img = Video.objects.get(pk=id).thumbnail
#     return HttpResponse(img, content_type="image/jpg")

