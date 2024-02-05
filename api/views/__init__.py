from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .base import BaseModelViewSet
from .site import SiteViewSet
from .camera_config import CameraConfigViewSet
from .profile import ProfileViewSet
from .recipe import RecipeViewSet
from .task import TaskViewSet
from .time_series import TimeSeriesViewSet
from .video import VideoViewSet, VideoSiteViewSet
from .device import DeviceViewSet
from users.models.institute import Institute

#
# @login_required()
# def switch_institute(request, institute_id):
#     institute_obj = Institute.objects.get(pk=institute_id)
#     if request.user.is_institute_member(institute_obj):
#         request.session[settings.INSTITUTE_SESSION_KEY] = institute_obj.pk
#     url_path = request.GET.get("next")
#     return redirect(url_path)
