from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework import status, renderers, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from api.serializers import DeviceSerializer, TaskFormSerializer
from api.models import Device, TaskFormStatus, TaskForm, DeviceStatus, DeviceFormStatus
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
        # get information about device
        params = request.data.dict()
        if not(params):
            # try to get them from query_params, usually with unit tests, they end up here
            params = request.query_params.dict()
        try:
            device = Device.objects.get(pk=kwargs["pk"])
            if not(request.user == device.creator):
                return Response(
                    data={"device_id": [f"Device {device.id} does not belong to user."]},
                    status=status.HTTP_403_FORBIDDEN,
                    content_type="application/json"
                )
        except:
            # if this is an entirely new device, then make a new device for this particular case
            params["creator"] = request.user
            params["id"] = kwargs["pk"]
            device = Device(**params)
        # update the device
        ip_address = request.META.get("REMOTE_ADDR")
        if ip_address:
            device.ip_address = ip_address
        device.last_seen = timezone.now()
        device.status = DeviceStatus(int(params.get("status")))
        device.form_status = DeviceFormStatus(int(params.get("form_status")))
        device.message = params.get("message")
        device.save()
        # query for new task forms for this particular device
        queryset = TaskForm.objects.filter(status=TaskFormStatus.NEW).filter(device=device)
        if len(queryset) == 0:
            return Response(
                data={"device_id": [f"No new configuration for Device {device.id}"]},
                status=status.HTTP_204_NO_CONTENT,
                content_type="application/json"
            )
        if len(queryset) == 1:
            task_form = queryset[0]
            serializer = TaskFormSerializer(task_form)
            # set status to SENT (will be set to REJECTED or ACCEPTED once validated on NodeORC)
            task_form.status = TaskFormStatus.SENT
            task_form.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"task_form": [f"There are multiple new task forms available for device {device.id}, delete them so that only one is available"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=['patch'], renderer_classes=[renderers.JSONRenderer])
    def patch_task_form(self, request, *args, **kwargs):
        """ Patch a task form to ACCEPTED or REJECTED """
        try:
            device = Device.objects.get(pk=kwargs["pk"])
            if not(request.user == device.creator):
                return Response(
                    data={"device_id": [f"Device {device.id} does not belong to user."]},
                    status=status.HTTP_403_FORBIDDEN,
                    content_type="application/json"
                )
        except:
            return Response(
                data={"device_id": [f"Device {kwargs['pk']} does not exist."]},
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json"
            )
        task_form_id = request.data.get("id")
        # get the status by status number
        task_status = TaskFormStatus(
            int(request.data.get("status"))
        )
        task_form = TaskForm.objects.get(pk=task_form_id)
        # patch the status
        task_form.status = task_status
        task_form.save()
        serializer = TaskFormSerializer(task_form)
        # print(f"URL: {request.build_absolute_uri(reverse('video'))}")
        return Response(serializer.data, status=status.HTTP_200_OK)






