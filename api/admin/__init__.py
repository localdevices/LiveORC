from django.contrib import admin
from ..models import Site, CameraConfig, Video, Task, Server, Profile, Recipe, TimeSeries

from .time_series import TimeSeriesAdmin
from .camera_config import CameraConfigAdmin
from .video import VideoInline, VideoAdmin
from .site import SiteAdmin
from .task import TaskAdmin
from .server import ServerAdmin

admin.site.register(Site, SiteAdmin)
admin.site.register(CameraConfig, CameraConfigAdmin)
admin.site.register(Profile)
admin.site.register(Recipe)
# admin.site.register(Project, ProjectAdmin)  # leave out for now, may become relevant for future geospatial applications
admin.site.register(Video, VideoAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TimeSeries, TimeSeriesAdmin)
