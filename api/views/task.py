from rest_framework import permissions, status
from rest_framework.response import Response

from api.serializers import TaskSerializer, TaskCreateSerializer
from api.models import Task, Video
from api.task_utils import get_task
from api.views import BaseModelViewSet


class TaskViewSet(BaseModelViewSet):
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
