from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from api.models import CameraConfig, Video
from api.admin import BaseAdmin, SiteUserFilter, BaseForm
import json
import pyorc


# Register your models here.
class VideoInline(admin.TabularInline):
    """
    Display filtered videos for given site or project inside admin view of site and project
    """
    model = Video
    extra = 3


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

    def filter_institute(self, request, qs):
        institutes = request.user.get_membership_institutes()
        return qs.filter(site__institute__in=institutes)


    def save_model(self, request, obj, form, change):
        request._files["json_file"].seek(0)
        form.instance.camera_config = json.load(request._files["json_file"])
        super().save_model(request, obj, form, change)

    def bounding_box_view(self, obj):
        return obj.bbox_view

