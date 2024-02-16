from django import forms

from api.admin import BaseAdmin, BaseForm
from api.admin import TaskInstituteFilter

from api.models import TaskForm, CameraConfig

class TaskFormForm(BaseForm):

    class Meta:
        model = TaskForm
        fields = ["device", "task_body"]

class TaskFormAdmin(BaseAdmin):

    form = TaskFormForm
    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            if obj.institute in request.user.get_membership_institutes():
                return True
        elif len(request.user.get_membership_institutes()) > 0:
            return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    ordering = ["-created_on"]
    list_filter = [TaskInstituteFilter]
    list_display = [
        "id",
        "created_on",
        "status_icon"
    ]

    # list_display = ["__all__"]

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(institute__in=institutes)


    def status_icon(self, obj):
        return obj.status_icon
    status_icon.short_description = "Status"
    status_icon.allow_tags = True
