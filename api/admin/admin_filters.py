from datetime import datetime
from dateutil.relativedelta import relativedelta
from rangefilter.filters import DateTimeRangeFilterBuilder

from django.contrib import admin

from api.models import Site
from users.models import Institute

default_end = datetime.now()
default_start = default_end - relativedelta(days=1)


datetimefilter = DateTimeRangeFilterBuilder(
    default_start=default_start,
    default_end=default_end
)


class InstituteOwnerFilter(admin.SimpleListFilter):
    title = "Filter owned institutes"
    parameter_name = "owner"

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            institutes = Institute.objects.all()
        else:
            institutes = Institute.filter(owner=request.user)

        return institutes.values_list("id", "name")


class VideoSiteUserFilter(admin.SimpleListFilter):
    title = "Filter sites"
    parameter_name = "camera_config__site__user"

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


class InstituteFilter(admin.SimpleListFilter):
    title = "Filter institutes"
    parameter_name = "site_institute"

    def lookups(self, request, model_admin):
        # filter the filter key for the current user. TODO: change in institute once issue 34 is resolved
        if request.user.is_superuser:
            institutes = Institute.objects.all()
        else:
            institutes = Institute.objects.filter(name__in=request.user.get_membership_institutes())

        return institutes.values_list("id", "name")

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(institute__id=value)


class VideoInstituteFilter(InstituteFilter):
    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(camera_config__site__institute__id=value)


class TaskInstituteFilter(InstituteFilter):
    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(video__camera_config__site__institute__id=value)



class SiteUserFilter(admin.SimpleListFilter):
    title = "Filter sites"
    parameter_name = "site_user"

    def lookups(self, request, model_admin):
        # filter the filter key for the institutes with memberships
        if request.user.is_superuser:
            sites = Site.objects.all()
        else:
            sites = Site.objects.filter(institute__in=request.user.get_membership_institutes())

        return sites.values_list("id", "name")

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(site__id=value)
