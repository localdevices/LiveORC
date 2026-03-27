from django.contrib import admin
from django.contrib.auth.models import Group
from api.models import (
    Site,
    CameraConfig,
    VideoConfig,
    Video,
    Task,
    TaskForm,
    Server,
    CrossSection,
    Recipe,
    TimeSeries,
    Device
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
from .cross_section import CrossSectionAdmin
from .video_config import VideoConfigAdmin
from .recipe import RecipeAdmin
from .video import VideoInline, VideoAdmin
from .site import SiteAdmin
from .device import DeviceAdmin
from .task import TaskAdmin
from .task_form import TaskFormAdmin
from .server import ServerAdmin

# initiate orc admin site with specific titles and logos
# admin.site.site_title = gettext_lazy("LiveOpenRiverCam")
# admin.site.site_header = gettext_lazy("LiveOpenRiverCam")
# admin.site.index_title = gettext_lazy("Admin dashboard")


admin.site.register(Site, SiteAdmin)
admin.site.register(CameraConfig, CameraConfigAdmin)
admin.site.register(VideoConfig, VideoConfigAdmin)
admin.site.register(CrossSection, CrossSectionAdmin)
admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(Project, ProjectAdmin)  # leave out for now, may become relevant for future geospatial applications
admin.site.register(Video, VideoAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskForm, TaskFormAdmin)
admin.site.register(TimeSeries, TimeSeriesAdmin)
admin.site.unregister(Group)

