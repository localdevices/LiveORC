from django.urls import path, include
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from api.serializers.auth import EmailTokenObtainPairSerializer
from api.views import (
    VersionView,
    SiteViewSet,
    CrossSectionViewSet,
    # ProfileViewSet,
    RecipeViewSet,
    CameraConfigViewSet,
    VideoConfigViewSet,
    VideoViewSet,
    VideoSiteViewSet,
    TimeSeriesViewSet,
    # TaskViewSet,
    DeviceViewSet
)

app_name = 'api'


router = routers.DefaultRouter()
router.register(r'site', SiteViewSet)
# router.register(r'cameraconfig', CameraConfigViewSet)
# router.register(r'profile', ProfileViewSet)
router.register(r'recipe', RecipeViewSet)
router.register(r'video', VideoViewSet)
router.register(r'device', DeviceViewSet)
# router.register(r'timeseries', TimeSeriesViewSet)

site_router = routers.NestedSimpleRouter(router, r'site', lookup='site')
site_router.register(r'video', VideoSiteViewSet, basename='site-video')
site_router.register(r'timeseries', TimeSeriesViewSet, basename='site-timeseries')
site_router.register(r'crosssection', CrossSectionViewSet, basename='site-crosssection')
site_router.register(r'cameraconfig', CameraConfigViewSet, basename='site-cameraconfig')
site_router.register(r'videoconfig', VideoConfigViewSet, basename='site-videoconfig')

video_router = routers.NestedSimpleRouter(site_router, r'video', lookup='video')
# video_router.register(r'task', TaskViewSet, basename='video-task')

urlpatterns = [
    path('version/', VersionView.as_view(), name='version'),
    path('token/', TokenObtainPairView.as_view(serializer_class=EmailTokenObtainPairSerializer), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('institute_switch/<int:institute_id>/', switch_institute),
    path('', include(router.urls)),
    path('', include(site_router.urls)),
    path('', include(video_router.urls)),

]
