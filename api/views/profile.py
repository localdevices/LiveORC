from rest_framework import viewsets, status
from rest_framework.response import Response
from LiveORC.utils.api.viewsets import InstitutionMixin
from api.serializers import ProfileSerializer, ProfileCreateSerializer
from api.models import Profile

class ProfileViewSet(InstitutionMixin, viewsets.ModelViewSet):
    """
    API endpoints that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    http_method_names = ["get", "post", "delete", "patch"]

    def get_serializer_class(self):
        if self.action == 'create':
            return ProfileCreateSerializer
        return ProfileSerializer

    def create(self, request, site_pk=None, *args, **kwargs):
        # insert the site
        data = request.data.copy()
        if not(data.get("site")):
            data["site"] = site_pk
        # replace the serializer
        serializer_class = ProfileSerializer
        # run create in the usual manner
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
