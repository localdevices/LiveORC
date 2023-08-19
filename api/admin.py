from django.contrib import admin
from django.contrib.gis import admin as gisadmin
from .models import Site, Profile, Recipe, CameraConfig, Video, Task, Server, Project, WaterLevel


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


class CameraConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "get_site_name"]
    search_fields = ["name"]
    list_filter = ["site"]
    inlines = [VideoInline]
    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ["name", "description"]
    inlines = [VideoInline]

class TaskAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

class ServerAdmin(admin.ModelAdmin):
    list_display = ["type", "url", "end_point", "wildcard", "frequency"]

class VideoAdmin(admin.ModelAdmin):
    list_display = ["get_site_name", "created_at", "timestamp", "water_level", "thumbnail_preview"]  #  "thumbnail",
    readonly_fields = ('thumbnail_preview', 'video_preview',)
    list_filter = ["created_at", "timestamp"]
    @admin.display(ordering='camera_config__site__name', description="Site")
    def get_site_name(self, obj):
        return obj.camera_config.site.name

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview
    thumbnail_preview.short_description = 'Keyframe preview'
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
