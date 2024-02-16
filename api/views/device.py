from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework import status, renderers, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from api.serializers import DeviceSerializer, TaskFormSerializer
from api.models import Device, TaskFormStatus, TaskForm
from api.views import BaseModelViewSet
from users.models import Institute


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

    @action(detail=True, methods=['get'], renderer_classes=[renderers.JSONRenderer])
    def get_task_form(self, request, *args, **kwargs):
        """Check if a new task form is available for the device that is logging in """
        try:
            device = Device.objects.get(pk=kwargs["pk"])
        except:
            # if this nis an entirely new device, then make a new device for this particular case
            params = request.query_params.dict()
            params["creator"] = request.user
            device = Device(**params)
        # update the device
        ip_address = request.META.get("REMOTE_ADDR")
        if ip_address:
            device.ip_address = ip_address
        device.last_seen = timezone.now()
        device.save()
        # query for new task forms for this particular device
        queryset = TaskForm.objects.filter(status=TaskFormStatus.NEW).filter(device=device)
        if len(queryset) == 0:
            return Response(
                data={"device_id": [f"No new configuration for Device {request.query_params['device_id']}"]},
                status=status.HTTP_204_NO_CONTENT,
                content_type="application/json"
            )
        if len(queryset) == 1:
            task_form = queryset[0]
            serializer = TaskFormSerializer(task_form)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"task_form": [f"There are multiple new task forms available for device {request.query_params['device_id']}, delete them so that only one is available"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
