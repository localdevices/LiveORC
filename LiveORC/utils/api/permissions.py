from rest_framework import permissions


class IsOwnerOrReadOnlyAsInstitute(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read (GET, HEAD, OPTIONS) permissions are allowed if either the user is the creator of the object, or belongs to the same
        # institute as the creator. Institute of course cannot be None!
        if request.method in permissions.SAFE_METHODS:
            if (
                    request.user.institute == obj.creator.institute and request.user.institute is not None
            ) or request.user == obj.creator:
                return True
            return False
        # Write permissions are only allowed to the creator of the object.
        return obj.creator == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS and request.user.members.filter(
                instution=obj.institution
        ).exists():
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.institution.owner == request.user