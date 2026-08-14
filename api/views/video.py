import mimetypes

from django.http import HttpResponse
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status, permissions, renderers
from rest_framework.decorators import action
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
    API endpoints that allows videos to be added
    """
    queryset = Video.objects.all().order_by('-timestamp')
    serializer_class = VideoSerializer
    # permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

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
        # log_file = self.get_object().log_file
        # if os.path.isfile(log_file):
        #     with open(log_file, 'r') as f:
        #         log_data = f.read()
        # else:
        #     log_data = f"No log file found for video {self.get_object().id} at site {self.get_object().video_config.site.name}."
        log_data = f"dummy log for video {self.get_object().id}"
        return HttpResponse(log_data, content_type='text/plain')

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def netcdf_1d(self, request, *args, **kwargs):
        # retrieve the path to the 1d netcdf file
        # netcdf_1d_file = self.get_object().netcdf_1d
        netcdf_1d_file = "dummy_file.nc"
        # come up with a logical name for the netcdf file for downloading
        netcdf_filename = f"{self.get_object().video_config.site.name}_{self.get_object().video_config.name}_1d.nc"
        with open(netcdf_1d_file, 'rb') as f:
            netcdf_data = f.read()
        response = HttpResponse(netcdf_data, content_type='application/x-netcdf')
        response['Content-Disposition'] = f'attachment; filename="{netcdf_filename}"'
        return response

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def netcdf_2d(self, request, *args, **kwargs):
        # retrieve the path to the 2d netcdf file
        # netcdf_2d_file = self.get_object().netcdf_2d
        netcdf_2d_file = "dummy_file.nc"
        # come up with a logical name for the netcdf file for downloading
        netcdf_filename = f"{self.get_object().video_config.site.name}_{self.get_object().video_config.name}_2d.nc"
        with open(netcdf_2d_file, 'rb') as f:
            netcdf_data = f.read()
        response = HttpResponse(netcdf_data, content_type='application/x-netcdf')
        response['Content-Disposition'] = f'attachment; filename="{netcdf_filename}"'
        return response


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

