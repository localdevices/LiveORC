import mimetypes
import urllib

from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import storages
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status, permissions, renderers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from api.serializers import VideoSerializer
from api.models import Video, Task, VideoStatus
# from api.task_utils import get_task
from api.views import BaseModelViewSet

_SITE_PK_PARAM = OpenApiParameter(
    name='site_pk', type=OpenApiTypes.INT, location=OpenApiParameter.PATH
)


class VideoViewSet(BaseModelViewSet):
    """
    API endpoints that allows videos to be added, changed and viewed
    """
    queryset = Video.objects.all().order_by('-timestamp')
    serializer_class = VideoSerializer
    # permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

    # At the top of the VideoViewSet class
    ALLOWED_RESULT_KEYS = {'2d', '2d_mask', '1d', '2d_ugrid'}

    def get_queryset(self):
        # video can also be retrieved nested per site, by filtering on the site of the camera config via video config.
        return Video.objects.filter(video_config__site__id=self.kwargs['site_pk'])

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

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def log_file(self, request, *args, **kwargs):
        # first retrieve the path to the log file
        video = self.get_object()
        # get log string
        log_data = video.get_log_file()
        if log_data is None:
            return HttpResponse(
                f"No log file found for video {video.id} at site {video.video_config.site.name}.",
                content_type='text/plain', status=404
            )
        return HttpResponse(log_data, content_type='text/plain')

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def result_1d(self, request, *args, **kwargs):
        # retrieve the video
        video = self.get_object()
        # download result
        return video.download_result('1d')

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def result_2d(self, request, *args, **kwargs):
        # retrieve the video
        video = self.get_object()
        # download result
        return video.download_result('2d')

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def result_2d_mask(self, request, *args, **kwargs):
        # retrieve the video
        video = self.get_object()
        # download result
        return video.download_result('2d_mask')

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def result_2d_ugrid(self, request, *args, **kwargs):
        # retrieve the video
        video = self.get_object()
        # download result
        return video.download_result('2d_ugrid')

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def result_all(self, request, *args, **kwargs):
        # retrieve the video
        video = self.get_object()
        # download result
        return video.download_all_results()


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
        # try:
        #     self._process_result_files(instance, request)
        # except ValidationError:
        #     # Re-raise validation errors as-is
        #     instance.delete()
        #     raise
        # except Exception as e:
        #     # Clean up the video if result file processing fails
        #     instance.delete()
        #     raise ValidationError({"result_files": f"File upload failed: {str(e)}"})
        # TODO bring back once ORCOS task creation is supported.
        # check if a time series instance was found during creation
        # if instance.is_ready_for_task:
        #     # launch creation of a new task
        #     instance.create_task(request=request)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Override update to handle result file uploads.
        Result files should be sent as 'result_<key>' (e.g., 'result_2d', 'result_2d_mask')
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # # Process result files if any
        # try:
        #     self._process_result_files(instance, request)
        # except ValidationError:
        #     # Re-raise validation errors as-is
        #     raise
        # except Exception as e:
        #     # Clean up the video if result file processing fails
        #     raise ValidationError({"result_files": f"File upload failed: {str(e)}"})
        return Response(serializer.data)

    # TODO: Bring back once ORCOS task creation is supported
    # @action(detail=True, methods=['post'], renderer_classes=[renderers.StaticHTMLRenderer])
    # def create_task(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     task = get_task(instance, request, *args, **kwargs)
    #     return redirect('api:video-list')


@extend_schema(parameters=[_SITE_PK_PARAM])
class VideoSiteViewSet(VideoViewSet):
    """
    API endpoints that allows videos to be edited
    """
    http_method_names = ["get", "patch", "head", "delete"]

