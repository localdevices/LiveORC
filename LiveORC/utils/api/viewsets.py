from django.core.exceptions import FieldError
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from .permissions import IsInstitutionMember


class InstitutionMixin(object):
    permission_classes = (
        permissions.IsAuthenticated,
        IsInstitutionMember,
    )

    def get_queryset(self):
        queryset = super(InstitutionMixin, self).get_queryset()
        institutions = [institution_member.institution for institution_member in self.request.user.members.all()]
        try:
            queryset = queryset.filter(institution__in=institutions)
        except FieldError:
            queryset = queryset.filter(site__institution__in=institutions)
        except Exception:
            pass
        return queryset



