from django.contrib.gis import admin as gisadmin
from ..admin import WaterLevelInline


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
