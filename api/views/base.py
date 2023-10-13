# define a base ModelViewSet with modifications needed for all api models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from LiveORC.utils.api.permissions import IsOwnerOrReadOnlyAsInstitute

class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyAsInstitute]

    def perform_create(self, serializer):
        # add the creator upon saving
        serializer.save(creator=self.request.user)