from django.contrib import admin
from api.admin import BaseAdmin

class TaskAdmin(BaseAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    ordering = ["-video__timestamp"]

    list_display = [
        "id",
        "thumbnail_preview",
        "get_video_timestamp",
        "progress_bar",
        "video_status"
    ]

    def thumbnail_preview(self, obj):
        return obj.video.thumbnail_preview
    thumbnail_preview.short_description = 'Thumbnail'
    thumbnail_preview.allow_tags = True

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(video__camera_config_obj__site__institute__in=institutes)


    def get_video_timestamp(self, obj):
        return obj.video.timestamp
    get_video_timestamp.short_description = 'Timestamp'
    get_video_timestamp.allow_tags = True

    def video_status(self, obj):
        return obj.video.play_button
    video_status.short_description = "Status"
    video_status.allow_tags = True
