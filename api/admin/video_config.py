from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.urls import reverse

# from api import callback_utils
from api.admin import BaseAdmin, BaseForm, SiteUserFilter
from api.models import VideoConfig # , Device, TaskForm, TaskFormStatus  # removed to avoid Tasks for now
# from api.task_utils import get_task_form
# from api.views.video_config import CALLBACK_FUNCTIONS_FORM

# TODO replace for ORC-OS interface once implemented
# callback_options = [
#     {
#         "name": c.lstrip("get_form_callback_"),
#         "value": c,
#         "docstring": getattr(callback_utils, c).__doc__.split("Parameters")[0].strip()
#         if getattr(callback_utils, c).__doc__
#         else "",
#     }
#     for c in CALLBACK_FUNCTIONS_FORM
# ]

# callback_discharge = [
#     {"name": c["name"].replace("_", " ").capitalize(), "value": c["value"], "docstring": c["docstring"]}
#     for c in callback_options
#     if c["name"].startswith("discharge")
# ]

# callback_video = [
#     {"name": c["name"].replace("_", " ").capitalize(), "value": c["value"], "docstring": c["docstring"]}
#     for c in callback_options
#     if c["name"].startswith("video")
# ]


class VideoConfigForm(BaseForm):
    class Meta:
        model = VideoConfig
        fields = "__all__"


class VideoConfigAdmin(BaseAdmin):
    fieldsets = [
        (
            "User input",
            {
                "fields": [
                    "name",
                    "camera_config",
                    "recipe",
                    "cross_section",
                    "cross_section_wl",
                    # "rvec",
                    # "tvec",
                ]
            },
        )
    ]

    list_display = ["name", "get_site_name"]
    search_fields = ["name"]
    list_filter = [SiteUserFilter]
    form = VideoConfigForm

    @admin.display(ordering="site__name", description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # devices_list = [{"name": str(device), "id": device.id} for device in Device.objects.all()]
        extra_context = extra_context or {}
        # extra_context["device_options"] = devices_list
        # extra_context["callback_discharge"] = callback_discharge
        # extra_context["callback_video"] = callback_video
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        # TODO replace with ORC-OS interface once implemented
        # my_urls = [path("<int:pk>/send_form", self.admin_site.admin_view(self.send_form_view))]
        # return my_urls + urls
        return urls

    def filter_institute(self, request, qs):
        institutes = request.user.get_membership_institutes()
        return qs.filter(site__institute__in=institutes)

    # TODO replace with ORC-OS interface once implemented
    # def send_form_view(self, request, pk):
    #     if request.method != "POST":
    #         return HttpResponseRedirect(reverse("admin:api_videoconfig_change", args=(pk,)))

    #     device_id = request.POST.get("device")
    #     try:
    #         device = Device.objects.get(pk=device_id)
    #         if request.user != device.creator:
    #             messages.error(request, f"Device {device_id} is not owned by you")
    #             return HttpResponseRedirect(reverse("admin:api_videoconfig_change", args=(pk,)))
    #     except Device.DoesNotExist:
    #         messages.error(request, f"Device {device_id} does not exist")
    #         return HttpResponseRedirect(reverse("admin:api_videoconfig_change", args=(pk,)))

    #     queryset = TaskForm.objects.filter(status=TaskFormStatus.NEW).filter(device=device)
    #     if len(queryset) > 0:
    #         messages.error(request, f"A new task form for device {device_id} already exists.")
    #         return HttpResponseRedirect(reverse("admin:api_videoconfig_change", args=(pk,)))

    #     query_callbacks = [request.POST.get("discharge"), request.POST.get("video")]
    #     query_callbacks = [cb for cb in query_callbacks if cb]
    #     instance = self.get_object(request, pk)
    #     if instance is None:
    #         messages.error(request, "VideoConfig does not exist.")
    #         return HttpResponseRedirect(reverse("admin:api_videoconfig_changelist"))
    #     if not instance.recipe:
    #         messages.error(request, "VideoConfig does not have a recipe.")
    #         return HttpResponseRedirect(reverse("admin:api_videoconfig_change", args=(pk,)))
    #     if not instance.cross_section:
    #         messages.error(request, "VideoConfig does not have a cross section.")
    #         return HttpResponseRedirect(reverse("admin:api_videoconfig_change", args=(pk,)))

    #     task_form = get_task_form(instance, query_callbacks)
    #     record = TaskForm(task_body=task_form, device=device, creator=request.user, institute=instance.institute)
    #     record.save()
    #     return HttpResponseRedirect(reverse("admin:api_taskform_change", args=(record.id,)))
