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
    list_display = ["get_site_name", "timestamp", "h", "fraction_velocimetry", "q_50", 'thumbnail_preview']
    list_filter = ["site__name"]
    readonly_fields = ('image_preview', )
    list_filter = ["site", "timestamp"]

    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def get_readonly_fields(self, request, obj=None):
        # prevent that the file or camera config can be changed afterwards. That is very risky and can lead to inconsistent
        # model records
        if obj:
            return (
                *self.readonly_fields,
                "site",
                "timestamp",
                "h",
                "q_05",
                "q_25",
                "q_50",
                "q_75",
                "q_95",
                "wetted_surface",
                "wetted_perimeter",
                "fraction_velocimetry"
            )
        return self.readonly_fields


    def thumbnail_preview(self, obj):
        return obj.video.thumbnail_preview
    thumbnail_preview.short_description = 'Thumbnail'
    thumbnail_preview.allow_tags = True

    def image_preview(self, obj):
        return obj.video.image_preview
    image_preview.short_description = 'Video result (if available)'
    image_preview.allow_tags = True
