from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from django.contrib.gis import admin as gisadmin
from ..models import CameraConfig, Video

import json
import pyorc


# Register your models here.
class VideoInline(admin.TabularInline):
    """
    Display filtered videos for given site or project inside admin view of site and project
    """
    model = Video
    extra = 3


class CameraConfigForm(forms.ModelForm):
    json_file = forms.FileField()
    class Meta:
        model = CameraConfig
        fields = ["name", "site", "server", "recipe", "profile", "camera_config"] #, "bbox"]


    def clean(self):
        super().clean()
        # open the json file and try to parse
        if "json_file" in self.files:
            data = json.load(self.files["json_file"])
            try:
                pyorc.CameraConfig(**data)
                # see if you can make a camera config object
            except BaseException as e:
                raise ValidationError(f"Problem with Camera Configuration: {e}")

class CameraConfigAdmin(gisadmin.GISModelAdmin):
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
    list_filter = ["site"]
    form = CameraConfigForm
    # inlines = [VideoInline]
    readonly_fields = ["bounding_box_view", "height", "width", "resolution", "window_size", "bbox"]
    formfield_overrides = {}
    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def save_model(self, request, obj, form, change):
        request._files["json_file"].seek(0)
        form.instance.camera_config = json.load(request._files["json_file"])
        super().save_model(request, obj, form, change)

    def bounding_box_view(self, obj):
        return obj.bbox_view

