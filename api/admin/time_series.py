from django.contrib import admin
from django import forms
from import_export.admin import ExportActionModelAdmin
from import_export.forms import ExportForm

from api.models import TimeSeries, Site
from api.admin import BaseAdmin, BaseForm
from api.admin import SiteUserFilter
from api.resources import TimeSeriesResource


class CustomExportForm(ExportForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=True
    )
    start_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            required=False,
            help_text="Start date and time in local timezone"
        )
    )
    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="End date and time in local timezone",
    )

    def clean(self):
        # check start and end dates on form
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date and time cannot be earlier than start date and time.")
        return cleaned_data


class TimeSeriesForm(BaseForm):

    class Meta:
        model = TimeSeries
        fields = "__all__"


class TimeSeriesInline(admin.TabularInline):
    """
    Display water level for given site in admin view of site
    """
    model = TimeSeries
    extra = 5


class TimeSeriesAdmin(ExportActionModelAdmin, BaseAdmin):
    resource_classes = [TimeSeriesResource]
    export_form_class = CustomExportForm
    list_display = ["get_site_name", "timestamp", "str_h", "str_fraction_velocimetry", "str_q_50", 'thumbnail_preview']
    list_filter = ["site__name"]
    readonly_fields = (
        "image_preview",
        "str_q_05",
        "str_q_25",
        "str_q_50",
        "str_q_75",
        "str_q_95",
        "str_fraction_velocimetry",
        "link_video"
    )
    list_filter = [SiteUserFilter, "timestamp"]
    fieldsets = [
        (None, {"fields": ["image_preview", "site", "timestamp", "link_video"]}),
        (
            "Values", {
                "fields":
                    [
                        "h",
                        "str_q_05",
                        "str_q_25",
                        "str_q_50",
                        "str_q_75",
                        "str_q_95",
                        "wetted_surface",
                        "wetted_perimeter",
                        "str_fraction_velocimetry"
                    ]
            }
        )
    ]
    form = TimeSeriesForm

    @admin.display(ordering='site__name', description="Site")
    def get_site_name(self, obj):
        return obj.site.name

    def get_readonly_fields(self, request, obj=None):
        # prevent that the file or camera config can be changed afterwards. That is very risky and can lead to
        # inconsistent model records
        if obj:
            return (
                *self.readonly_fields,
                "site",
                "timestamp",
                "link_video",
                "h",
                "str_q_05",
                "str_q_25",
                "str_q_50",
                "str_q_75",
                "str_q_95",
                "wetted_surface",
                "wetted_perimeter",
                "str_fraction_velocimetry"
            )
        return self.readonly_fields

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(site__institute__in=institutes)

    def link_video(self, obj):
        return obj.link_video

    def thumbnail_preview(self, obj):
        return obj.video.thumbnail_preview
    thumbnail_preview.short_description = 'Thumbnail'
    thumbnail_preview.allow_tags = True

    def image_preview(self, obj):
        return obj.video.image_preview
    image_preview.short_description = 'Video result (if available)'
    image_preview.allow_tags = True

    def str_h(self, obj):
        if obj.h:
            return round(obj.h, 3)
    str_h.short_description = 'Water level [m]'
    str_h.allow_tags = True

    def str_q_05(self, obj):
        if obj.q_05:
            return round(obj.q_05, 2)
    str_q_05.short_description = 'Discharge 5% [m3/s]'
    str_q_05.allow_tags = True

    def str_q_25(self, obj):
        if obj.q_25:
            return round(obj.q_25, 2)
    str_q_25.short_description = 'Discharge 25% [m3/s]'
    str_q_25.allow_tags = True

    def str_q_50(self, obj):
        if obj.q_50:
            return round(obj.q_50, 2)
    str_q_50.short_description = 'Discharge 50% [m3/s]'
    str_q_50.allow_tags = True

    def str_q_75(self, obj):
        if obj.q_75:
            return round(obj.q_75, 2)
    str_q_75.short_description = 'Discharge 75% [m3/s]'
    str_q_75.allow_tags = True

    def str_q_95(self, obj):
        if obj.q_95:
            return round(obj.q_95, 2)
    str_q_95.short_description = 'Discharge 95% [m3/s]'
    str_q_95.allow_tags = True

    def str_fraction_velocimetry(self, obj):
        if obj.fraction_velocimetry:
            return round(obj.fraction_velocimetry, 2)
    str_fraction_velocimetry.short_description = 'Fraction velocimetry [%]'
    str_fraction_velocimetry.allow_tags = True
