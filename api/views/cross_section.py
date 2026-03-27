from rest_framework import status
from rest_framework.response import Response
from api.serializers import CrossSectionSerializer, CrossSectionCreateSerializer
from api.models import CrossSection
from api.views import BaseModelViewSet


class CrossSectionViewSet(BaseModelViewSet):
    """API endpoints that allow cross sections to be viewed or edited."""

    queryset = CrossSection.objects.all()
    serializer_class = CrossSectionSerializer
    http_method_names = ["get", "post", "delete", "patch"]

    def get_serializer_class(self):
        if self.action == 'create':
            return CrossSectionCreateSerializer
        return CrossSectionSerializer

    def create(self, request, site_pk=None, *args, **kwargs):
        # insert the site
        data = request.data.copy()
        if not(data.get("site")):
            data["site"] = site_pk
        # replace the serializer
        serializer_class = CrossSectionSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    # # Backward-compatible alias so older imports/routes can remain operational.
    # ProfileViewSet = CrossSectionViewSet
