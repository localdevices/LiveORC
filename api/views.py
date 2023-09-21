from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework import viewsets, permissions, renderers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Site, Profile, Recipe, CameraConfig, Video, TimeSeries, Task
from .serializers import (
    SiteSerializer,
    ProfileSerializer,
    ProfileCreateSerializer,
    RecipeSerializer,
    CameraConfigSerializer,
    CameraConfigCreateSerializer,
    VideoSerializer,
    TimeSeriesSerializer,
    TimeSeriesCreateSerializer,
    TaskSerializer,
    TaskCreateSerializer
)
import mimetypes


class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows sites to be viewed or edited.
    """
    queryset = Site.objects.all().order_by('name')
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ["post", "get", "patch", "delete"]

class CameraConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows camera configurations to be viewed or edited.
    """
    queryset = CameraConfig.objects.all().order_by('name')
    serializer_class = CameraConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CameraConfigCreateSerializer
        return CameraConfigSerializer

    def create(self, request, site_pk=None, *args, **kwargs):
        # insert the site
        if not(request.data.get("site")):
            request.data["site"] = site_pk
        # replace the serializer
        serializer_class = CameraConfigSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "patch"]

    def get_serializer_class(self):
        if self.action == 'create':
            return ProfileCreateSerializer
        return ProfileSerializer

    def create(self, request, site_pk=None, *args, **kwargs):
        # insert the site
        if not(request.data.get("site")):
            request.data["site"] = site_pk
        # replace the serializer
        serializer_class = ProfileSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows recipes to be viewed or edited.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "patch"]


class TimeSeriesViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows time series to be viewed or edited.
    """
    queryset = TimeSeries.objects.all()
    serializer_class = TimeSeriesSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "patch"]


    def get_serializer_class(self):
        if self.action == 'create':
            return TimeSeriesCreateSerializer
        return TimeSeriesSerializer

    def create(self, request, site_pk=None, *args, **kwargs):
        # insert the site
        if not(request.data.get("site")):
            request.data["site"] = site_pk
        # replace the serializer
        serializer_class = TimeSeriesSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        # video can also be retrieved nested per site, by filtering on the site of the cameraconfig property.
        return TimeSeries.objects.filter(site=self.kwargs['site_pk'])

    # def create(self, request, *args, **kwargs):


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows tasks to be viewed or edited.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "patch"]

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

    def create(self, request, site_pk=None, video_pk=None, *args, **kwargs):
        # insert the site
        if not(request.data.get("site")):
            request.data["site"] = site_pk
        if not(request.data.get("video")):
            request.data["video"] = video_pk
        # replace the serializer
        serializer_class = TaskSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allows videos to be added
    """
    queryset = Video.objects.all().order_by('-timestamp')
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

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

class VideoSiteViewSet(VideoViewSet):
    """
    API endpoints that allows videos to be edited
    """
    http_method_names = ["get", "patch", "head", "delete"]



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

