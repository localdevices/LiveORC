from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from api.views import SiteViewSet, ProfileViewSet, RecipeViewSet, CameraConfigViewSet, VideoViewSet, TimeSeriesViewSet, TaskViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from . import views


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'site', SiteViewSet)
router.register(r'cameraconfig', CameraConfigViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'recipe', RecipeViewSet)
router.register(r'video', VideoViewSet)
router.register(r'timeseries', TimeSeriesViewSet)
router.register(r'task', TaskViewSet)


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs_swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
