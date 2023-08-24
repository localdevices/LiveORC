from django.contrib import admin
from ..models import Video
class VideoInline(admin.TabularInline):
    """
    Display filtered videos for given site or project inside admin view of site and project
    """
    model = Video
    extra = 3

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

