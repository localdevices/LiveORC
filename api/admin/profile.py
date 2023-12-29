from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from api.models import Profile
from api.admin import BaseAdmin, SiteUserFilter

import json
import pyorc


# Register your models here.

class ProfileForm(forms.ModelForm):
    geojson_file = forms.FileField()
    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        # if not self.request.user.get_active_membership():
        #     raise forms.ValidationError("You Must have an institute to continue")
        # open the json file and try to parse
        if "geojson_file" in self.files:
            try:
                self.files["geojson_file"].seek(0)
                geo = json.load(self.files["geojson_file"])
                # verify that geojson contains the right data
                data, crs = pyorc.cli.cli_utils.read_shape(geojson=geo)
            except BaseException as e:
                raise ValidationError(f"Problem with profile file: {e}")

class ProfileAdmin(BaseAdmin):
    class Media:
        js = (
            'https://cdn.jsdelivr.net/npm/ol@v7.2.2/dist/ol.js',
            'gis/js/OLMapWidget.js',
              )
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/ol@v7.2.2/ol.css',
                'gis/css/ol3.css',
            )
        }
    fieldsets = [
        ("User input", {"fields": ["name", "site", "timestamp", "geojson_file"]}),
        ("Resulting non-editable profile information", {
            "fields": [
                "profile_view",
                "crs",
                "multipoint",
            ]}
         )
    ]
    list_display = ["name", "timestamp", "get_site_name"]
    search_fields = ["site"]
    list_filter = [SiteUserFilter]
    form = ProfileForm
    readonly_fields = ["profile_view", "crs", "multipoint"]
    formfield_overrides = {}
    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(site__institute__in=institutes)


    def save_model(self, request, obj, form, change):
        request._files["geojson_file"].seek(0)
        form.instance.data = json.load(request._files["geojson_file"])
        super().save_model(request, obj, form, change)

    def profile_view(self, obj):
        return obj.profile_view

