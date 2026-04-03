import json

import pyorc
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from api.admin import BaseAdmin, BaseForm, SiteUserFilter
from api.models import CameraConfig


class CameraConfigForm(BaseForm):
    json_file = forms.FileField(required=False)

    class Meta:
        model = CameraConfig
        fields = ["name", "site", "server", "allowed_dt", "end_date", "data"]

    def clean(self):
        super().clean()
        if "json_file" in self.files:
            data = json.load(self.files["json_file"])
            try:
                pyorc.CameraConfig(**data)
            except BaseException as exc:
                raise ValidationError(f"Problem with camera configuration: {exc}")


class CameraConfigAdmin(BaseAdmin):
    class Media:
        js = (
            "https://cdn.jsdelivr.net/npm/ol@v7.2.2/dist/ol.js",
            "gis/js/OLMapWidget.js",
        )
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/ol@v7.2.2/ol.css",
                "gis/css/ol3.css",
            )
        }

    fieldsets = [
        ("User input", {"fields": ["name", "site", "server", "allowed_dt", "end_date", "json_file"]}),
        (
            "Resulting non-editable camera configuration",
            {
                "fields": [
                    "bbox",
                    "height",
                    "width",
                    "resolution",
                    "window_size",
                    "bounding_box_view",
                    "bounding_box_3d_view"
                ]
            },
        ),
    ]

    list_display = ["name", "get_site_name"]
    search_fields = ["name"]
    list_filter = [SiteUserFilter]
    form = CameraConfigForm
    readonly_fields = ["bounding_box_view", "bounding_box_3d_view", "height", "width", "resolution", "window_size", "bbox"]

    @admin.display(ordering="site__name", description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def filter_institute(self, request, qs):
        institutes = request.user.get_membership_institutes()
        return qs.filter(site__institute__in=institutes)

    def save_model(self, request, obj, form, change):
        if "json_file" in request.FILES:
            request.FILES["json_file"].seek(0)
            form.instance.data = json.load(request.FILES["json_file"])
        super().save_model(request, obj, form, change)

    @admin.display(description="Camera calibration geographical view")
    def bounding_box_view(self, obj):
        return obj.bbox_view

    @admin.display(description="Camera calibration 3D view")
    def bounding_box_3d_view(self, obj):
        return obj.bbox_plot_3d
