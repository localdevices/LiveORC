from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from django.contrib.gis import admin as gisadmin
from .models import Site, Profile, Recipe, CameraConfig, Video, Task, Server, Project, WaterLevel

import json
import pyorc
from pyproj import CRS, Transformer
import shapely



# Register your models here.
class VideoInline(admin.TabularInline):
    """
    Display filtered videos for given site or project inside admin view of site and project
    """
    model = Video
    extra = 3



class WaterLevelInline(admin.TabularInline):
    """
    Display water level for given site in admin view of site
    """
    model = WaterLevel
    extra = 5


class SiteAdmin(gisadmin.GISModelAdmin):
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    search_fields = ["name"]
    list_display = ["name", "geom"]
    inlines = [WaterLevelInline]
    search_fields = ["name"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

class CameraConfigForm(forms.ModelForm):
    json_file = forms.FileField()
    class Meta:
        model = CameraConfig
        fields = ["name", "site", "server", "recipe", "profile", "bbox"]


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

    # def save(self):
    #     data = json.load(self.files["json_file"])
    #     # fill in the parts
    #     self.data["height"] = data["height"]

class CameraConfigAdmin(gisadmin.GISModelAdmin):
    fieldsets = [
        ("User input", {"fields": ["name", "end_date", "site", "server", "recipe", "profile", "json_file"]}),
        ("Resulting non-editable camera configuration", {"fields": ["bbox", "height", "width", "camera_calibration", "gcps", "window_size", "resolution", "crs_wkt"]})
    ]

    list_display = ["name", "get_site_name"]
    search_fields = ["name"]
    list_filter = ["site"]
    form = CameraConfigForm
    inlines = [VideoInline]
    readonly_fields = ["height", "width", "camera_calibration", "gcps", "window_size", "resolution", "crs_wkt", "end_date"]
    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def save_model(self, request, obj, form, change):
        request._files["json_file"].seek(0)
        data = json.load(request._files["json_file"])
        # fill in the missing components from the parsed json
        form.instance.height = data["height"]
        form.instance.width = data["width"]
        form.instance.camera_calibration = {
            "camera_matrix": data["camera_matrix"],
            "dist_coeffs": data["dist_coeffs"],
            "stabilize": data["stabilize"] if "stabilize" in data else None
        }
        form.instance.gcps = data["gcps"]
        form.instance.window_size = data["window_size"]
        form.instance.resolution = data["resolution"]
        form.instance.bbox_wkt = data["bbox"]
        if "crs" in data:
            form.instance.crs_wkt = data["crs"]
            transformer = Transformer.from_crs(
                CRS.from_user_input(data["crs"]),
                CRS.from_epsg(4326),
                always_xy=True).transform

            polygon = shapely.wkt.loads(data["bbox"])
            polygon = shapely.ops.transform(transformer, polygon)
            form.instance.bbox = polygon.wkt
        if "is_nadir" in data:
            form.instance.is_nadir = data["is_nadir"]
        if "lens_position" in data:
            lp = data["lens_position"]
            if lp is not None:
                form.instance.lens_position = {
                    "x": lp[0],
                    "y": lp[1],
                    "z": lp[2]
                }

        super().save_model(request, obj, form, change)


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ["name", "description"]
    inlines = [VideoInline]

class TaskAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

class ServerAdmin(admin.ModelAdmin):
    list_display = ["type", "url", "end_point", "wildcard", "frequency"]

class VideoAdmin(admin.ModelAdmin):
    list_display = ["get_site_name", "created_at", "timestamp", "water_level", "thumbnail_preview"]
    readonly_fields = ('video_preview',)
    list_filter = ["created_at", "timestamp"]
    @admin.display(ordering='camera_config__site__name', description="Site")
    def get_site_name(self, obj):
        return obj.camera_config.site.name

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview
    thumbnail_preview.short_description = 'Thumbnail'
    thumbnail_preview.allow_tags = True

    def video_preview(self, obj):
        return obj.video_preview
    video_preview.short_description = 'video preview'
    video_preview.allow_tags = True


class WaterLevelAdmin(admin.ModelAdmin):
    list_display = ["get_site_name", "timestamp", "value"]
    list_filter = ["site__name"]
    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name


admin.site.register(Site, SiteAdmin)
admin.site.register(CameraConfig, CameraConfigAdmin)
admin.site.register(Profile)
admin.site.register(Recipe)
# admin.site.register(Project, ProjectAdmin)  # leave out for now, may become relevant for future geospatial applications
admin.site.register(Video, VideoAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(WaterLevel, WaterLevelAdmin)
