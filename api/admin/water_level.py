from django.contrib import admin

from django.contrib.gis import admin as gisadmin
from ..models import WaterLevel



class WaterLevelInline(admin.TabularInline):
    """
    Display water level for given site in admin view of site
    """
    model = WaterLevel
    extra = 5


# Register your models here.
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



class WaterLevelAdmin(admin.ModelAdmin):
    list_display = ["get_site_name", "timestamp", "value"]
    list_filter = ["site__name"]
    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name
