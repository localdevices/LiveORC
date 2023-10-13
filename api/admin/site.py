from django.contrib.gis import admin as gisadmin
from .base import BaseAdmin
# from users.models.institute import Institute, InstituteMember
from LiveORC.utils.api.viewsets import InstitutionMixin


# Register your models here.
class SiteAdmin(BaseAdmin):
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Coordinates", {"fields": ["geom"]})
    ]
    search_fields = ["name"]
    list_display = ["name", "geom"]

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     institutions = [team.institution for team in InstitutionMember.objects.filter(member=request.user)]
    #     return qs.filter(institution__in=institutions)

    # def save_model(self, request, obj, form, change):
    #     super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # super users can see everything. Return all
            return qs
        # Non-super users can only see their own models, and the models from other users within their institute
        qs_institute = qs.filter(creator__institute=request.user.institute) | qs.filter(creator=request.user)
        return qs_institute# + qs_user
        # return qs_user


    # def get_queryset(self):
    #     queryset = super(InstitutionMixin, self).get_queryset()
    #     institutions = [institution_member.institution for institution_member in self.request.user.members.all()]
    #     try:
    #         queryset = queryset.filter(institute__in=institutions)
    #     except FieldError:
    #         queryset = queryset.filter(site__institute__in=institutions)
    #     except Exception:
    #         pass
    #     return queryset
