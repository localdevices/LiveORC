import sys
import django
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api import __version__


class VersionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "version": __version__,
            "django_version": django.__version__,
            "python_version": sys.version,
        })
