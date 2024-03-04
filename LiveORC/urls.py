"""
URL configuration for LiveORC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
# from django.contrib.admin import AdminSite
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

## CODE BELOW IS TO REORDER MENU ITEMS, CAN BE FINISHED WHEN ADMIN VIEW IS DONE
# def get_app_list(self, request):
#     """
#     Modified version of original get_app_list that reorders the required parts
#     """
#     ordering = {
#         "Sites": 1,
#         "Camera configs": 2,
#         "Recipes": 3,
#         "Profiles": 4,
#         "Videos": 5,
#         "Projects": 6,
#         "Servers": 7,
#         "Tasks": 8,
#         "Groups": 9,
#         "Users": 10
#     }
#     app_dict = self._build_app_dict(request)
#     # a.sort(key=lambda x: b.index(x[0]))
#     # Sort the apps alphabetically.
#     app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
#
#     # Sort the models alphabetically within each app.
#     for app in app_list:
#         app['models'].sort(key=lambda x: ordering[x['name']])
#     return app_list
#
# admin.AdminSite.get_app_list = get_app_list

urlpatterns = [
    path('', include('users.urls')),
    # path('', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include('api.urls', namespace='api')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs_swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )