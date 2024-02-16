from django.contrib.gis import admin
from django import forms

from api.models import Device

class DeviceForm(forms.ModelForm):

    class Meta:
        model = Device
        fields = "__all__"


class DeviceAdmin(admin.GISModelAdmin):
    def has_add_permission(self, request):
        return False

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
        return False


    form = DeviceForm
    # list_filter = [TaskInstituteFilter]
    #
    # list_display = [
    #     "id",
    #     "thumbnail_preview",
    #     "get_video_timestamp",
    #     "progress_bar",
    #     "video_status"
    # ]

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(institute__in=institutes)

