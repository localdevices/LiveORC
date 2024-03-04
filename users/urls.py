from django.urls import path
from .views import FirstUserCreateView

urlpatterns = [
    path('', FirstUserCreateView.as_view(), name='firstuser'),
]
