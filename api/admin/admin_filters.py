from datetime import datetime
from dateutil.relativedelta import relativedelta
from rangefilter.filters import DateTimeRangeFilterBuilder

from django.contrib import admin

from api.models import Site


default_end = datetime.now()
default_start = default_end - relativedelta(days=1)


datetimefilter = DateTimeRangeFilterBuilder(
    default_start=default_start,
    default_end=default_end
)


class VideoSiteUserFilter(admin.SimpleListFilter):
    title = "Filter sites"
    parameter_name = "camera_config__site_user"

    def lookups(self, request, model_admin):
        # filter the filter key for the current user. TODO: change in institute once issue 34 is resolved
        if request.user.is_superuser:
            sites = Site.objects.all()
        else:
            sites = Site.objects.filter(creator=request.user)

        return sites.values_list("id", "name")

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(camera_config__site__id=value)


class SiteUserFilter(admin.SimpleListFilter):
    title = "Filter sites"
    parameter_name = "site_user"

    def lookups(self, request, model_admin):
        # filter the filter key for the current user. TODO: change in institute once issue 34 is resolved
        if request.user.is_superuser:
            sites = Site.objects.all()
        else:
            sites = Site.objects.filter(institute=request.user.get_active_institute())

        return sites.values_list("id", "name")

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(site__id=value)
