from rest_framework import status, renderers
from rest_framework.response import Response
from rest_framework.decorators import action

from api.serializers import CameraConfigSerializer, CameraConfigCreateSerializer
from api.models import CameraConfig
from api.views import BaseModelViewSet


class CameraConfigViewSet(BaseModelViewSet):
    """
    API endpoints that allows camera configurations to be viewed or edited.
    """
    queryset = CameraConfig.objects.all().order_by('name')
    serializer_class = CameraConfigSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CameraConfigCreateSerializer
        return CameraConfigSerializer

    def create(self, request, site_pk=None, *args, **kwargs):
        # insert the site
        data = request.data.copy()
        if not(data.get("site")):
            data["site"] = site_pk
        if not(data.get("creator")):
            data["creator"] = request.user.pk
        # replace the serializer
        serializer_class = CameraConfigSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=True, methods=['post'], renderer_classes=[renderers.StaticHTMLRenderer])
    def create_task(self, request, device_id, *args, **kwargs):
        instance = self.get_object()
        # task = get_task_form(instance, request, *args, **kwargs)
        # print(f"URL: {request.build_absolute_uri(reverse('video'))}")
        return Response(instance.data, status=status.HTTP_200_OK)

