from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework import viewsets, permissions, renderers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Site, Profile, Recipe, CameraConfig, Video, TimeSeries, Task, VideoStatus
from .task_utils import get_task
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
        data = request.data.copy()
        if not(data.get("site")):
            data["site"] = site_pk
        # replace the serializer
        serializer_class = CameraConfigSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=data)
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
        data = request.data.copy()
        if not(data.get("site")):
            data["site"] = site_pk
        # replace the serializer
        serializer_class = ProfileSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=data)
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
        data = request.data.copy()
        if not(request.data.get("site")):
            data["site"] = site_pk
        # replace the serializer
        serializer_class = TimeSeriesSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        # video can also be retrieved nested per site, by filtering on the site of the cameraconfig property.
        return TimeSeries.objects.filter(site=self.kwargs['site_pk'])


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
        data = request.data.copy()
        if not(data.get("site")):
            data["site"] = site_pk
        if not(data.get("video")):
            data["video"] = video_pk
        # get the video
        try:
            video_instance = Video.objects.get(id=video_pk)

            data["task_body"] = get_task(video_instance, request, *args, **kwargs)
            # replace the serializer
            serializer_class = TaskSerializer
            # run create in the usual manner
            kwargs.setdefault('context', self.get_serializer_context())
            serializer = serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
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


    def create(self, request, *args, **kwargs):
        """
        Override create to make sure that if a tiume series with a water level is found, a new task is launched to
        process the video

        Parameters
        ----------
        request
        args
        kwargs

        Returns
        -------

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # self.get_object does not work because a new video is posted on a open end point, without association to a site
        instance = Video.objects.get(id=serializer.data["id"])
        # check if a time series instance was found during creation
        if instance.time_series:
            if instance.status == VideoStatus.NEW and instance.time_series.q_50 is None and instance.time_series.h is not None:
                # launch creation of a new task
                task_body = get_task(instance, request, serialize=False,*args, **kwargs)
                task = {
                    "id": task_body["id"],
                    "task_body": task_body,
                    "video": instance
                }
                Task.objects.create(**task)
                # update the Video instance
                instance.status = VideoStatus.QUEUE
                instance.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=True, methods=['post'], renderer_classes=[renderers.StaticHTMLRenderer])
    def create_task(self, request, *args, **kwargs):
        instance = self.get_object()
        task = get_task(instance, request, *args, **kwargs)
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

