from api.admin import BaseAdmin,BaseForm
from api.admin import TaskInstituteFilter
from api.models import Task


class TaskForm(BaseForm):
    class Meta:
        model = Task
        fields = "__all__"


class TaskAdmin(BaseAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # if obj:
        #     if obj.institute in request.user.get_membership_institutes():
        #         return True
        # elif len(request.user.get_membership_institutes()) > 0:
        #     return True

    def has_delete_permission(self, request, obj=None):
        return True

    form = TaskForm
    ordering = ["-video__timestamp"]
    list_filter = [TaskInstituteFilter]

    list_display = [
        "id",
        "thumbnail_preview",
        "get_video_timestamp",
        "progress_bar",
        "video_status",
        "status_msg"
    ]

    def thumbnail_preview(self, obj):
        return obj.video.thumbnail_preview
    thumbnail_preview.short_description = 'Thumbnail'
    thumbnail_preview.allow_tags = True

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(video__camera_config__site__institute__in=institutes)

    def get_video_timestamp(self, obj):
        return obj.video.timestamp
    get_video_timestamp.short_description = 'Timestamp'
    get_video_timestamp.allow_tags = True

    def video_status(self, obj):
        return obj.video.play_button
    video_status.short_description = "Status"
    video_status.allow_tags = True
