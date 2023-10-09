from django.contrib import admin
from django.utils.translation import gettext_lazy
from ..models import Site, CameraConfig, Video, Task, Server, Profile, Recipe, TimeSeries, Institution, InstitutionMember

from .time_series import TimeSeriesAdmin
from .camera_config import CameraConfigAdmin
from .profile import ProfileAdmin
from .video import VideoInline, VideoAdmin
from .site import SiteAdmin
from .task import TaskAdmin
from .server import ServerAdmin

# initiate orc admin site with specific titles and logos

admin.site.site_title = gettext_lazy("LiveOpenRiverCam")
admin.site.site_header = gettext_lazy("LiveOpenRiverCam")
admin.site.index_title = gettext_lazy("Admin dashboard")


admin.site.register(Site, SiteAdmin)
admin.site.register(CameraConfig, CameraConfigAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Recipe)
# admin.site.register(Project, ProjectAdmin)  # leave out for now, may become relevant for future geospatial applications
admin.site.register(Video, VideoAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TimeSeries, TimeSeriesAdmin)
admin.site.register(Institution)
admin.site.register(InstitutionMember)
