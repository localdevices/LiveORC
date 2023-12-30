from api.admin import BaseInstituteAdmin, BaseForm
from api.models import Site


class SiteForm(BaseForm):

    class Meta:
        model = Site
        fields = "__all__"


class SiteAdmin(BaseInstituteAdmin):
    form = SiteForm
    fieldsets = [
        (None, {"fields": ["name", "institute"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    super_admin_fieldsets = [
        (None, {"fields": ["name", "institute"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    search_fields = ["name"]
    list_display = ["name", "geom"]

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return self.super_admin_fieldsets
        return self.fieldsets

