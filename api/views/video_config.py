from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import renderers, status
from rest_framework.decorators import action
from rest_framework.response import Response

# from api import callback_utils
from api.models import Device, TaskForm, VideoConfig
from api.serializers import TaskFormSerializer, VideoConfigCreateSerializer, VideoConfigSerializer, VideoConfigUpdateSerializer
# from api.task_utils import get_task_form
from api.views import BaseModelViewSet

# collect names of all callback functions valid for task forms
# CALLBACK_FUNCTIONS_FORM = [f for f in dir(callback_utils) if f.startswith("get_form_callback")]


class VideoConfigViewSet(BaseModelViewSet):
    """API endpoints that allow video configurations to be viewed or edited."""

    queryset = VideoConfig.objects.all().order_by("name")
    serializer_class = VideoConfigSerializer
    http_method_names = ["get", "post", "delete", "patch"]

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        site_pk = self.kwargs.get("site_pk")
        if site_pk:
            return self.queryset.filter(camera_config__site_id=site_pk)
        return self.queryset

    def get_serializer_class(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        if self.action == "create":
            return VideoConfigCreateSerializer
        if self.action in ["update", "partial_update"]:
            return VideoConfigUpdateSerializer
        return VideoConfigSerializer

    def create(self, request, site_pk=None, *args, **kwargs):
        data = request.data.copy()
        if not data.get("site"):
            data["site"] = site_pk
        if not data.get("creator"):
            data["creator"] = request.user.pk

        kwargs.setdefault("context", self.get_serializer_context())
        serializer = VideoConfigSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, site_pk=None, *args, **kwargs):
        """Override update to prevent site and creator from being updated, even if included in request body."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()
        if not data.get("site"):
            data["site"] = int(site_pk)
        if not data.get("creator"):
            data["creator"] = instance.creator.pk
        data["creator"] = instance.creator.pk

        kwargs.setdefault("context", self.get_serializer_context())
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # headers = self.get_success_headers(serializer.data)
        return Response(serializer.data) #, status=status.HTTP_200_OK, headers=headers)
    
    # TODO: once orc-os api is connected, bring back task generation in a new approach with celery agents.
    # @extend_schema(
    #     description="Create a task form for a specified device based on this video configuration",
    #     parameters=[
    #         OpenApiParameter(
    #             name="device_id",
    #             type=str,
    #             required=True,
    #             location=OpenApiParameter.QUERY,
    #             description="UUID of device to provide task form to",
    #         ),
    #         OpenApiParameter(
    #             name="callback",
    #             type=str,
    #             required=True,
    #             enum=[c.lstrip("get_form_callback_") for c in CALLBACK_FUNCTIONS_FORM],
    #             location=OpenApiParameter.QUERY,
    #             description="Name of callback function to add",
    #         ),
    #     ],
    # )
    # @action(detail=True, methods=["post"], renderer_classes=[renderers.JSONRenderer])
    # def create_task(self, request, *args, **kwargs):
    #     if "device_id" not in request.query_params:
    #         return Response(
    #             data={"device_id": ["This field is required."]},
    #             status=status.HTTP_400_BAD_REQUEST,
    #             content_type="application/json",
    #         )

    #     try:
    #         device = Device.objects.get(pk=request.query_params["device_id"])
    #         if request.user != device.creator:
    #             return Response(
    #                 data={"device_id": [f"Device {request.query_params['device_id']} does not belong to user."]},
    #                 status=status.HTTP_403_FORBIDDEN,
    #                 content_type="application/json",
    #             )
    #     except Device.DoesNotExist:
    #         return Response(
    #             data={"device_id": [f"Device {request.query_params['device_id']} does not exist."]},
    #             status=status.HTTP_400_BAD_REQUEST,
    #             content_type="application/json",
    #         )

    #     if "callback" not in request.query_params:
    #         return Response(
    #             data={"callback": ["At least one callback must be provided"]},
    #             status=status.HTTP_400_BAD_REQUEST,
    #             content_type="application/json",
    #         )

    #     query_callbacks = [f"get_form_callback_{c}" for c in request.query_params.getlist("callback")]
    #     for callback in query_callbacks:
    #         if callback not in CALLBACK_FUNCTIONS_FORM:
    #             return Response(
    #                 data={
    #                     "callback": [
    #                         f"Callback {callback} is not available, choose from {[c.lstrip('get_form_callback_') for c in CALLBACK_FUNCTIONS_FORM]}"
    #                     ]
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST,
    #                 content_type="application/json",
    #             )

    #     instance = self.get_object()
    #     if not instance.recipe:
    #         return Response(
    #             data={"recipe": ["Video config does not contain a recipe."]},
    #             status=status.HTTP_400_BAD_REQUEST,
    #             content_type="application/json",
    #         )
    #     if not instance.cross_section:
    #         return Response(
    #             data={"cross_section": ["Video config does not contain a cross section."]},
    #             status=status.HTTP_400_BAD_REQUEST,
    #             content_type="application/json",
    #         )

    #     task_form = get_task_form(instance, query_callbacks)
    #     record = TaskForm(
    #         id=task_form["id"],
    #         task_body=task_form,
    #         device=device,
    #         creator=request.user,
    #         institute=instance.institute,
    #     )
    #     record.save()
    #     serializer = TaskFormSerializer(record)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
