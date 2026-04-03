from rest_framework import status
from rest_framework.response import Response

from api.models import CameraConfig
from api.serializers import CameraConfigCreateSerializer, CameraConfigSerializer, CameraConfigUpdateSerializer
from api.views import BaseModelViewSet


class CameraConfigViewSet(BaseModelViewSet):
    """API endpoints that allow camera configurations to be viewed or edited."""

    queryset = CameraConfig.objects.all().order_by("name")
    serializer_class = CameraConfigSerializer
    http_method_names = ["get", "post", "delete", "patch"]

    def get_serializer_class(self):
        if self.action == "create":
            return CameraConfigCreateSerializer
        if self.action in ["update", "partial_update"]:
            return CameraConfigUpdateSerializer
        return CameraConfigSerializer

    def create(self, request, site_pk=None, *args, **kwargs):
        data = request.data.copy()
        if not data.get("site"):
            data["site"] = site_pk
        if not data.get("creator"):
            data["creator"] = request.user.pk

        kwargs.setdefault("context", self.get_serializer_context())
        serializer = CameraConfigSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
