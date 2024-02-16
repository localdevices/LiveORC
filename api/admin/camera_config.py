from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.urls import path
from django.shortcuts import redirect, reverse

from api.models import CameraConfig, Video, Device, TaskForm, TaskFormStatus
from api.admin import BaseAdmin, SiteUserFilter, BaseForm
from api.task_utils import get_task_form
from api.views.camera_config import CALLBACK_FUNCTIONS_FORM

callback_options = [{"name": c.lstrip("get_form_callback_"), "value": c} for c in CALLBACK_FUNCTIONS_FORM]

callback_discharge = [{"name": c["name"].replace("_", " ").capitalize(), "value": c["value"]} for c in callback_options if c["name"].startswith("discharge")]
callback_video = [{"name": c["name"].replace("_", " ").capitalize(), "value": c["value"]} for c in callback_options if c["name"].startswith("video")]

import json
import pyorc


# Register your models here.
class VideoInline(admin.TabularInline):
    """
    Display filtered videos for given site or project inside admin view of site and project
    """
    model = Video
    extra = 3

# class TaskFormActionForm(admin.helpers.ActionForm):
#     choices = [("blue", "Blue"), ("green", "Green"), ("black", "Black")]
#
#     device = forms.ModelChoiceField(
#         queryset=Device.objects.all(),
#         required=True,
#         to_field_name="device"
#     )
#     callbacks = forms.MultipleChoiceField(
#         required=True,
#         widget=forms.CheckboxSelectMultiple,
#         choices=choices
#
#     )

class CameraConfigForm(BaseForm):
    json_file = forms.FileField()

    class Meta:
        model = CameraConfig
        fields = ["name", "site", "server", "recipe", "profile", "camera_config"] #, "bbox"]

    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super(CameraConfigForm, self).__init__(*args, **kwargs)


    def clean(self):
        super().clean()
        # if not self.request.user.get_active_membership():
        #     raise forms.ValidationError("You Must have an institute to continue")
        # open the json file and try to parse
        if "json_file" in self.files:
            data = json.load(self.files["json_file"])
            try:
                pyorc.CameraConfig(**data)
                # see if you can make a camera config object
            except BaseException as e:
                raise ValidationError(f"Problem with Camera Configuration: {e}")

class CameraConfigAdmin(BaseAdmin):
    class Media:
        js = (
            'https://cdn.jsdelivr.net/npm/ol@v7.2.2/dist/ol.js',
            'gis/js/OLMapWidget.js',
              )
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/ol@v7.2.2/ol.css',
                'gis/css/ol3.css',
            )
        }
    fieldsets = [
        ("User input", {"fields": ["name", "end_date", "site", "allowed_dt", "server", "recipe", "profile", "json_file"]}),
        ("Resulting non-editable camera configuration", {
            "fields": [
                "bbox",
                "height",
                "width",
                "resolution",
                "window_size",
                "bounding_box_view"
            ]}
         )
    ]

    def post(self, request, pk, *args, **kwargs):
        print("CHECK")
    def response_post_save_change(self, request, obj):
        print("CHECK")

    def change_view(
            self,
            request,
            object_id,
            form_url="",
            extra_context=None
    ):
        # get devices with ids
        devices_list = [
            {"name": str(device), "id": device.id} for device in Device.objects.all()
        ]
        options_list = ['Option 1', 'Option 2', 'Option 3']
        extra_context = extra_context or {}
        extra_context['device_options'] = devices_list
        extra_context['callback_discharge'] = callback_discharge
        extra_context['callback_video'] = callback_video
        return super(CameraConfigAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def has_add_permission(self, request):
        True

    def has_change_permission(self, request, obj=None):
        # once made, you can only delete a cam config
        return True

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            if obj.institute in request.user.get_membership_institutes():
                return True
        elif len(request.user.get_membership_institutes()) > 0:
            return True


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/send_form", self.admin_site.admin_view(self.send_form_view)),
        ]
        return my_urls + urls

    list_display = ["name", "get_site_name"]
    search_fields = ["name"]
    list_filter = [SiteUserFilter]
    form = CameraConfigForm
    # inlines = [VideoInline]
    readonly_fields = ["bounding_box_view", "height", "width", "resolution", "window_size", "bbox"]
    formfield_overrides = {}

    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def has_create_form_permission(self, request, obj=None):
        """TODO, ensure this is only ok with owned device and owned objects"""
        return True

    def filter_institute(self, request, qs):
        institutes = request.user.get_membership_institutes()
        return qs.filter(site__institute__in=institutes)

    def send_form_view(self, request, pk):
        if request.method == "POST":
            # get the data
            device_id = request.POST.get("device")
            try:
                device = Device.objects.get(pk=device_id)
                if not (request.user == device.creator):
                    messages.error(request, f"Device {device_id} is not owned by you")
                    return HttpResponseRedirect(reverse("admin:api_cameraconfig_change", args=(pk, )))
            except:
                messages.error(request, f"Device {device_id} does not exist")
                # return redirect('admin/api/cameraconfig')
                return HttpResponseRedirect(reverse("admin:api_cameraconfig_change", args=(pk, )))
            # check if a NEW task form is already available. Do not allow having more than one NEW in the queue
            queryset = TaskForm.objects.filter(status=TaskFormStatus.NEW).filter(device=device)
            if len(queryset) > 0:
                messages.error(request, f"A new task form for device {device_id} already exists. If you want to cancel this task form, please first delete it.")
                return HttpResponseRedirect(reverse("admin:api_cameraconfig_change", args=(pk, )))

            # collect the callbacks
            query_callbacks = [
                request.POST.get("discharge"),
                request.POST.get("video")
            ]
            instance = self.get_object(request, pk)
            task_form = get_task_form(instance, query_callbacks)
            record = TaskForm(
                task_body=task_form,
                device=device,
                creator=request.user,
                institute=instance.institute
            )
            record.save()
            return HttpResponseRedirect(reverse("admin:api_taskform_change", args=(record.id, )))
            #
                # return HttpResponseBadRequest(f"Device {device_id} does not exist.")
                # # return Response(
                #     data={"device_id": [f"Device {request.query_params['device_id']} does not exist."]},
                #     status=status.HTTP_400_BAD_REQUEST,
                #     # content_type="application/json"
                # )

        print("HELLO THERE")

    def save_model(self, request, obj, form, change):
        request._files["json_file"].seek(0)
        form.instance.camera_config = json.load(request._files["json_file"])
        super().save_model(request, obj, form, change)

    def bounding_box_view(self, obj):
        return obj.bbox_view

