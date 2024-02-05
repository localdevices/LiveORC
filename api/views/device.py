from rest_framework import permissions
from api.serializers import DeviceSerializer
from api.models import Device
from api.views import BaseModelViewSet
from django_filters.rest_framework import DjangoFilterBackend


class DeviceViewSet(BaseModelViewSet):
    """
    API endpoints that allows devices to be viewed or edited.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "patch"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['institute']

    def get_queryset(self):
        """
        Optionally restricts the returned recipes to a given institute,
        by filtering against an `institute` query parameter in the URL.
        """
        queryset = Device.objects.all()
        institute = self.request.query_params.get('institute', None)
        if self.request.user.is_superuser:
            return queryset
        if institute:
            queryset = queryset.filter(institute=institute)
        return queryset.none()

