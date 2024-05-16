from api.admin import BaseInstituteAdmin, BaseForm
from api.models import Site


class SiteForm(BaseForm):

    class Meta:
        model = Site
        fields = "__all__"

# Register your models here.
class SiteAdmin(BaseInstituteAdmin):
    class Media:
        js = (
            "https://code.jquery.com/jquery-3.7.1.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js",
            "https://cdn.jsdelivr.net/npm/chart.js@4.4.0",
            "https://cdn.jsdelivr.net/npm/hammerjs@2.0.8",
            "https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/2.0.1/chartjs-plugin-zoom.js",
            "https://cdnjs.cloudflare.com/ajax/libs/chartjs-adapter-moment/1.0.1/chartjs-adapter-moment.min.js",
            "admin/js/timeseries.js"
        )

        css = {"all": ("admin/css/slider.css", )}
    form = SiteForm
    fieldsets = [
        (None, {"fields": ["name", "institute", "timeseries_chart"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    super_admin_fieldsets = [
        (None, {"fields": ["name", "institute", "timeseries_chart"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    search_fields = ["name"]
    list_display = ["name", "geom"]
    readonly_fields = ["timeseries_chart"]

    def timeseries_chart(self, obj):
        return obj.timeseries_chart

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return self.super_admin_fieldsets
        return self.fieldsets

