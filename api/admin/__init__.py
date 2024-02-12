from django.contrib import admin
from django.contrib.auth.models import Group
from api.models import (
    Site,
    CameraConfig,
    Video,
    Task,
    TaskForm,
    Server,
    Profile,
    Recipe,
    TimeSeries,
)

from .admin_filters import (
    VideoSiteUserFilter,
    SiteUserFilter,
    datetimefilter,
    InstituteFilter,
    TaskInstituteFilter,
    VideoInstituteFilter,
    InstituteOwnerFilter
)
from .base import BaseAdmin, BaseInstituteAdmin, BaseForm
from .time_series import TimeSeriesAdmin
from .camera_config import CameraConfigAdmin
from .profile import ProfileAdmin
from .recipe import RecipeAdmin
from .video import VideoInline, VideoAdmin
from .site import SiteAdmin
from .task import TaskAdmin
from .task_form import TaskFormAdmin
from .server import ServerAdmin

# initiate orc admin site with specific titles and logos
# admin.site.site_title = gettext_lazy("LiveOpenRiverCam")
# admin.site.site_header = gettext_lazy("LiveOpenRiverCam")
# admin.site.index_title = gettext_lazy("Admin dashboard")


admin.site.register(Site, SiteAdmin)
admin.site.register(CameraConfig, CameraConfigAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(Project, ProjectAdmin)  # leave out for now, may become relevant for future geospatial applications
admin.site.register(Video, VideoAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskForm, TaskFormAdmin)
admin.site.register(TimeSeries, TimeSeriesAdmin)
admin.site.unregister(Group)

