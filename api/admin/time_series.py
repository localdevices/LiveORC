from django.contrib import admin

from django.contrib.gis import admin as gisadmin
from ..models import TimeSeries



class TimeSeriesInline(admin.TabularInline):
    """
    Display water level for given site in admin view of site
    """
    model = TimeSeries
    extra = 5



class TimeSeriesAdmin(admin.ModelAdmin):
    list_display = ["get_site_name", "h", "fraction_velocimetry", "q_50"]
    list_filter = ["site__name"]
    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name
