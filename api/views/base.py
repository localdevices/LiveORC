# define a base ModelViewSet with modifications needed for all api models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from LiveORC.utils.api.permissions import IsOwnerOrReadOnlyAsInstitute


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    This BaseModelViewSet is for all models and model instancesin the API. These all have a 'creator' as non-editable
    field and should be visible only to people within the same institute or to the user that created them
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyAsInstitute]

    def perform_create(self, serializer):
        # only add the creator upon saving
        model_name = serializer.Meta.model.__name__
        site_obj = serializer.validated_data.get('site')
        camera_config_obj = serializer.validated_data.get('camera_config')
        if model_name == "CameraConfig" and site_obj:
            institute = site_obj.institute
            creator = site_obj.creator
        elif model_name == "Video" and camera_config_obj:
            institute = camera_config_obj.site.institute
            creator = camera_config_obj.site.creator
        else:
            institute = self.request.user.get_active_institute(self.request)
            creator = self.request.user
        serializer.save(creator=creator, institute=institute)
