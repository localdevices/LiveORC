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
    list_display = ["get_site_name", "timestamp", "str_h", "str_fraction_velocimetry", "str_q_50", 'thumbnail_preview']
    list_filter = ["site__name"]
    readonly_fields = (
        "image_preview",
        "str_q_05",
        "str_q_25",
        "str_q_50",
        "str_q_75",
        "str_q_95",
        "str_fraction_velocimetry",
        "link_video"
    )
    list_filter = ["site", "timestamp"]
    fieldsets = [
        (None, {"fields": ["image_preview", "site", "timestamp", "link_video"]}),
        ("Values", {"fields": ["h", "str_q_05", "str_q_25", "str_q_50", "str_q_75", "str_q_95", "wetted_surface", "wetted_perimeter", "str_fraction_velocimetry"]})
    ]

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
                "link_video",
                "h",
                "str_q_05",
                "str_q_25",
                "str_q_50",
                "str_q_75",
                "str_q_95",
                "wetted_surface",
                "wetted_perimeter",
                "str_fraction_velocimetry"
            )
        return self.readonly_fields

    def link_video(self, obj):
        return obj.link_video

    def thumbnail_preview(self, obj):
        return obj.video.thumbnail_preview
    thumbnail_preview.short_description = 'Thumbnail'
    thumbnail_preview.allow_tags = True

    def image_preview(self, obj):
        return obj.video.image_preview
    image_preview.short_description = 'Video result (if available)'
    image_preview.allow_tags = True

    def str_h(self, obj):
        if obj.h:
            return round(obj.h, 3)
    str_h.short_description = 'Water level [m]'
    str_h.allow_tags = True

    def str_q_05(self, obj):
        if obj.q_05:
            return round(obj.q_05, 2)
    str_q_05.short_description = 'Discharge 5% [m3/s]'
    str_q_05.allow_tags = True

    def str_q_25(self, obj):
        if obj.q_25:
            return round(obj.q_25, 2)
    str_q_25.short_description = 'Discharge 25% [m3/s]'
    str_q_25.allow_tags = True

    def str_q_50(self, obj):
        if obj.q_50:
            return round(obj.q_50, 2)
    str_q_50.short_description = 'Discharge 50% [m3/s]'
    str_q_50.allow_tags = True

    def str_q_75(self, obj):
        if obj.q_75:
            return round(obj.q_75, 2)
    str_q_75.short_description = 'Discharge 75% [m3/s]'
    str_q_75.allow_tags = True

    def str_q_95(self, obj):
        if obj.q_95:
            return round(obj.q_95, 2)
    str_q_95.short_description = 'Discharge 95% [m3/s]'
    str_q_95.allow_tags = True


    def str_fraction_velocimetry(self, obj):
        if obj.fraction_velocimetry:
            return round(obj.fraction_velocimetry, 2)
    str_fraction_velocimetry.short_description = 'Fraction velocimetry [%]'
    str_fraction_velocimetry.allow_tags = True
