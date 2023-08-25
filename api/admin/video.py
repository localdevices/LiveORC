from django.contrib import admin
from ..models import Video
class VideoInline(admin.TabularInline):
    """
    Display filtered videos for given site or project inside admin view of site and project
    """
    model = Video
    extra = 3

class VideoAdmin(admin.ModelAdmin):
    list_display = ["get_site_name", "created_at", "timestamp", "thumbnail_preview", "time_series"]
    readonly_fields = ('video_preview', 'get_site_name', 'thumbnail_preview', 'get_timestamp', 'get_water_level', 'get_discharge',)
    list_filter = ["created_at", "timestamp"]

    fieldsets = [
        ('Video details', {"fields": ["get_site_name", "timestamp", "thumbnail_preview"]}),
        ("Time series instance linked to the video", {
            "fields": [
                "get_timestamp",
                "get_water_level",
                "get_discharge",
            ]}
         )
    ]


    @admin.display(ordering='camera_config__site__name', description="Site")
    def get_site_name(self, obj):
        return obj.camera_config.site.name


    @admin.display(ordering='time_series__timestamp', description='Time stamp of related time series')
    def get_timestamp(self, obj):
        return obj.time_series.timestamp

    @admin.display(ordering='time_series__q_50', description='Discharge median [m3/s]')
    def get_discharge(self, obj):
        return obj.time_series.q_50

    @admin.display(ordering='time_series__h', description='Water level [m]')
    def get_water_level(self, obj):
        return obj.time_series.h


    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview
    thumbnail_preview.short_description = 'Thumbnail'
    thumbnail_preview.allow_tags = True

    def video_preview(self, obj):
        return obj.video_preview
    video_preview.short_description = 'video preview'
    video_preview.allow_tags = True

