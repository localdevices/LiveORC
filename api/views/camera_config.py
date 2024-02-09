from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, renderers
from rest_framework.response import Response
from rest_framework.decorators import action

from api.serializers import CameraConfigSerializer, CameraConfigCreateSerializer
from api.models import CameraConfig, Device
from api.views import BaseModelViewSet

from api.task_utils import get_task_form
from api import callback_utils

# collect names of all callback functions valid for
CALLBACK_FUNCTIONS_FORM = [f for f in dir(callback_utils) if f.startswith("get_form_callback")]


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


    @extend_schema(
        description="Create a task form for a specified device of the camera configuration",
        parameters=[
            OpenApiParameter(
                name='device_id',
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
                description='UUID of device to provide task form to'
            ),
            OpenApiParameter(
                name="callback",
                type=str,
                required=True,
                enum=[c.lstrip("get_form_callback_") for c in CALLBACK_FUNCTIONS_FORM],  # allowed names of callbacks
                location=OpenApiParameter.QUERY,
                description='name of callback function to add',

            ),
        ],
    )
    @action(detail=True, methods=['post'], renderer_classes=[renderers.JSONRenderer])
    def create_task(self, request, *args, **kwargs):
        if not "device_id" in request.query_params:
            return Response(
                data={"device_id": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json"
            )
        if not "callback" in request.query_params:
            return Response(
                data={"callback": ["At least one callback must be provided"]},
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json"
            )
        query_callbacks = [f"get_form_callback_{c}" for c in request.query_params.getlist("callback")]
        # check if callbacks are available
        for callback in query_callbacks:
            if not callback in CALLBACK_FUNCTIONS_FORM:
                return Response(
                    data={
                        "callback": [
                            f"Callback {callback.lsplit('get_form_callback')} is not available, choose from {[c.lstrip('get_form_callback_') for c in CALLBACK_FUNCTIONS_FORM]}"
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type="application/json"
                )
        instance = self.get_object()
        task_form = get_task_form(instance, query_callbacks, request, *args, **kwargs)
        # TODO: implement task_form in database
        # print(f"URL: {request.build_absolute_uri(reverse('video'))}")
        return Response(instance.data, status=status.HTTP_200_OK)

