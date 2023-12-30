from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.utils.translation import gettext_lazy


class CustomAdminConfig(AdminConfig):
    default_site = 'LiveORC.admin.CustomAdminSite'


class CustomAdminSite(admin.AdminSite):
    site_title = gettext_lazy("LiveOpenRiverCam")
    site_header = gettext_lazy("LiveOpenRiverCam")
    index_title = gettext_lazy("Admin dashboard")

    # def each_context(self, request):
    #     context = super(CustomAdminSite, self).each_context(request)
    #     if request.user.is_authenticated:
    #         context['active_institute'] = request.user.get_active_membership(request)
    #     else:
    #         context['active_institute'] = None
    #     return context