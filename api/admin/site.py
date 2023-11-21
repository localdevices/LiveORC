from api.admin import BaseAdmin
from ..forms.site import SiteForm


# Register your models here.
class SiteAdmin(BaseAdmin):
    form = SiteForm
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    search_fields = ["name"]
    list_display = ["name", "geom"]

