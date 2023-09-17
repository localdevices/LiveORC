from django.urls import path, include
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from api.views import SiteViewSet, ProfileViewSet, RecipeViewSet, CameraConfigViewSet, VideoViewSet, VideoSiteViewSet, TimeSeriesViewSet, TaskViewSet

app_name = 'api'


router = routers.DefaultRouter()
router.register(r'site', SiteViewSet)
router.register(r'cameraconfig', CameraConfigViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'recipe', RecipeViewSet)
router.register(r'video', VideoViewSet)
# router.register(r'timeseries', TimeSeriesViewSet)
router.register(r'task', TaskViewSet)

site_router = routers.NestedSimpleRouter(router, r'site', lookup='site')
site_router.register(r'video', VideoSiteViewSet, basename='site-video')
site_router.register(r'timeseries', TimeSeriesViewSet, basename='site-timeseries')

# time_series_router.register(r'video', VideoViewSet, basename='site-video')


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('', include(site_router.urls)),

]
