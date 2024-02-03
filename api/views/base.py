# define a base ModelViewSet with modifications needed for all api models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsOwnerOrReadOnlyAsInstitute
from rest_framework import status
from rest_framework.response import Response

from api.models import Site


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    This BaseModelViewSet is for all models and model instances in the API. These all have a 'creator' as non-editable
    field and should be visible only to people within the same institute or to the user that created them
    """
    permission_classes = [IsOwnerOrReadOnlyAsInstitute, IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if "site_pk" in self.kwargs:
            if not(request.user.is_institute_member(Site.objects.get(pk=self.kwargs["site_pk"]).institute) or self.request.user.is_superuser):
                return Response(
                {"detail": "You do not have permission to perform this action"},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().list(request, *args, **kwargs)


    def perform_create(self, serializer):
        # only add the creator upon saving
        # model_name = serializer.Meta.model.__name__
        # site_obj = serializer.validated_data.get('site')
        # camera_config_obj = serializer.validated_data.get('camera_config')
        # if model_name == "CameraConfig" and site_obj:
        #     serializer.save(creator=site_obj.creator)
        # elif model_name == "Video" and camera_config_obj:
        #     serializer.save(creator=camera_config_obj.site.creator)
        # else:

        serializer.save(creator=self.request.user)
