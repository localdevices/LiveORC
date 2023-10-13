from rest_framework import viewsets, status
from rest_framework.response import Response
from LiveORC.utils.api.viewsets import InstitutionMixin
from api.serializers import CameraConfigSerializer, CameraConfigCreateSerializer
from api.models import CameraConfig

class CameraConfigViewSet(InstitutionMixin, viewsets.ModelViewSet):
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
        # replace the serializer
        serializer_class = CameraConfigSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

