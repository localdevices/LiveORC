import mimetypes

from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework import status, permissions, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import VideoSerializer
from api.models import Video, Task, VideoStatus
from api.task_utils import get_task
from api.views import BaseModelViewSet


class VideoViewSet(BaseModelViewSet):
    """
    API endpoints that allows videos to be added
    """
    queryset = Video.objects.all().order_by('-timestamp')
    serializer_class = VideoSerializer
    # permission_classes = [permissions.IsAuthenticated]
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
    def thumbnail(self, request, *args, **kwargs):
        img = self.get_object().thumbnail
        mimetype, _ = mimetypes.guess_type(img.file.name)
        return HttpResponse(img, content_type=mimetype)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def image(self, request, *args, **kwargs):
        img = self.get_object().image
        mimetype, _ = mimetypes.guess_type(img.file.name)
        return HttpResponse(img, content_type=mimetype)

    def create(self, request, *args, **kwargs):
        """
        Override create to make sure that if a time series with a water level is found, a new task is launched to
        process the video.

        Parameters
        ----------
        request : request
        args : list
            pass to get_task
        kwargs : dict
            pass to get_task

        Returns
        -------

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # self.get_object does not work because a new video is posted on a open end point, without association to a site
        instance = Video.objects.get(id=serializer.data["id"])
        # check if a time series instance was found during creation

        if instance.is_ready_for_task:
            # launch creation of a new task
            instance.create_task(request=request)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



    @action(detail=True, methods=['post'], renderer_classes=[renderers.StaticHTMLRenderer])
    def create_task(self, request, *args, **kwargs):
        instance = self.get_object()
        task = get_task(instance, request, *args, **kwargs)
        return redirect('api:video-list')


class VideoSiteViewSet(VideoViewSet):
    """
    API endpoints that allows videos to be edited
    """
    http_method_names = ["get", "patch", "head", "delete"]

