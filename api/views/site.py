from api.serializers import SiteSerializer
from api.models import Site
from api.views import BaseModelViewSet
from rest_framework.response import Response
from users.models.base import get_object_or_none
from users.models.institute import Institute
from django_filters.rest_framework import DjangoFilterBackend


class SiteViewSet(BaseModelViewSet):

    """
    API endpoints that allows sites to be viewed or edited.
    """
    queryset = Site.objects.all().order_by('name')
    serializer_class = SiteSerializer

    http_method_names = ["post", "get", "patch", "delete"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['institute']

    def list(self, request, *args, **kwargs):
        institute = self.request.query_params.get('institute', None)
        institute_obj = get_object_or_none(Institute, id=institute)

        if request.user.is_superuser:
            raw_queryset = self.get_queryset()
        else:
            if institute_obj and institute_obj.has_member(request.user):
                raw_queryset = self.get_queryset().filter(institute__id=institute)
            else:
                raw_queryset = self.get_queryset().none()

        queryset = self.filter_queryset(raw_queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)