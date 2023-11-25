from api.admin import BaseAdmin


# Register your models here.
class SiteAdmin(BaseAdmin):
    class Media:
        js = (
            "https://code.jquery.com/jquery-3.7.1.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js",
            "https://cdn.jsdelivr.net/npm/chart.js@4.4.0",
            "https://cdn.jsdelivr.net/npm/hammerjs@2.0.8",
            "https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/2.0.1/chartjs-plugin-zoom.js",
            "https://cdnjs.cloudflare.com/ajax/libs/chartjs-adapter-moment/1.0.1/chartjs-adapter-moment.min.js"
        )

    fieldsets = [
        (None, {"fields": ["name", "timeseries_chart"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    search_fields = ["name"]
    list_display = ["name", "geom"]
    readonly_fields = ["timeseries_chart"]

    def timeseries_chart(self, obj):
        return obj.timeseries_chart