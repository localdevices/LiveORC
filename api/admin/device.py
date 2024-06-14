from django.contrib.gis import admin
from django import forms

from api.models import Device
from api.models import DeviceStatus, DeviceFormStatus
import nodeorc

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
        if request.user.is_superuser:
            return True
        return False

    form = DeviceForm
    # list_filter = [TaskInstituteFilter]
    #
    list_display = [
        "name",
        "id",
        "message",
        "status_ok",
        "form_status_ok",
        "version_synced"
    ]

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(institute__in=institutes)

    def status_ok(self, obj):
        """
        Check if device status is healthy
        """

        return obj.status == DeviceStatus.HEALTHY
    status_ok.boolean = True
    status_ok.allow_tags = True

    def form_status_ok(self, obj):
        """
        Check if currently active form of device is functional
        """

        return obj.form_status == DeviceFormStatus.VALID_FORM
    form_status_ok.boolean = True
    form_status_ok.allow_tags = True


    def version_synced(self, obj):
        """
        Check if currently active form of device is functional
        """

        return obj.nodeorc_version == nodeorc.__version__
    version_synced.boolean = True
    version_synced.allow_tags = True
