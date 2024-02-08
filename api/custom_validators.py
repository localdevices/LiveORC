from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from users.models import User


def institute_validator(institute, user):
    # if institute is not None
    if institute:
        owned_institutes = [m.institute for m in user.get_owned_institute_memberships()]
        if not (institute in owned_institutes):
            raise PermissionDenied()
    return


class InstituteOwned:
    requires_context = True

    def __call__(self, value, serializer_field):
        if "institute" in value:
            owned_institutes = [m.institute for m in serializer_field.context["request"].user.get_owned_institute_memberships()]
            if not (value["institute"] in owned_institutes):
                raise serializers.ValidationError(f'You do not own institute {value["institute"]}')


class SiteOwned:
    requires_context = True

    def __call__(self, value, serializer_field):
        if "site" in value:
            user = User.objects.get(pk=serializer_field.initial_data["creator"])
            owned_institutes = [m.institute for m in user.get_owned_institute_memberships()]
            if not (value["site"].institute in owned_institutes):
                raise serializers.ValidationError(f'You do not own institute {value["site"].institute}')

