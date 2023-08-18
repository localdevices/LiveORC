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
    inlines = [WaterLevelInline]
    list_filter = ["geom"]
    search_fields = ["name"]


class CameraConfigAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["site"]
    inlines = [VideoInline]


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ["name", "description"]
    inlines = [VideoInline]

class TaskAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


admin.site.register(Site, SiteAdmin)
admin.site.register(CameraConfig, CameraConfigAdmin)
admin.site.register(Profile)
admin.site.register(Recipe)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Video)
admin.site.register(Server)
admin.site.register(Task, TaskAdmin)
