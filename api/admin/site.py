from django import forms
from api.admin import BaseAdmin
from api.models import Site


class SiteForm(forms.ModelForm):

    class Meta:
        model = Site
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SiteForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.get_active_institute():
            raise forms.ValidationError("You Must have an institute to continue")


# Register your models here.
class SiteAdmin(BaseAdmin):
    form = SiteForm
    fieldsets = [
        (None, {"fields": ["name"]}),
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

