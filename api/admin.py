from django.contrib import admin
from .models import Site

# Register your models here.
class SiteAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Coordinates", {"fields": ["x", "y", "crs"]})
    ]
    search_fields = ["name"]


admin.site.register(Site, SiteAdmin)
