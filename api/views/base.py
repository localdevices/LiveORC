# define a base ModelViewSet with modifications needed for all api models
from rest_framework import viewsets
from LiveORC.utils.api.viewsets import InstitutionMixin

class BaseModelViewSet(InstitutionMixin, viewsets.ModelViewSet):
    def perform_create(self, serializer):
        # add the creator upon saving
        serializer.save(creator=self.request.user)