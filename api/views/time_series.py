from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from LiveORC.utils.api.viewsets import InstitutionMixin
from api.serializers import TimeSeriesSerializer, TimeSeriesCreateSerializer
from api.models import TimeSeries, Task, VideoStatus
from api.task_utils import get_task

class TimeSeriesViewSet(InstitutionMixin, viewsets.ModelViewSet):
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
        # look for a video instance linked to the time series
        instance = TimeSeries.objects.get(id=serializer.data["id"])
        if hasattr(instance, "video"):
            video_instance = instance.video
            if video_instance.is_ready_for_task:
                # launch creation of a new task
                task_body = get_task(video_instance, request, serialize=False,*args, **kwargs)
                task = {
                    "id": task_body["id"],
                    "task_body": task_body,
                    "video": video_instance
                }
                Task.objects.create(**task)
                # update the Video instance
                video_instance.status = VideoStatus.QUEUE
                video_instance.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        # video can also be retrieved nested per site, by filtering on the site of the cameraconfig property.
        return TimeSeries.objects.filter(site=self.kwargs['site_pk'])

