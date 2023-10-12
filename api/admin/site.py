from django.contrib.gis import admin as gisadmin
from .time_series import TimeSeriesInline
from api.models.institution import Institution, InstitutionMember


# Register your models here.
class SiteAdmin(gisadmin.GISModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "institution"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    search_fields = ["name"]
    list_display = ["name", "geom"]
    inlines = [TimeSeriesInline]

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     institutions = [team.institution for team in InstitutionMember.objects.filter(member=request.user)]
    #     return qs.filter(institution__in=institutions)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
