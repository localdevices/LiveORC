from rest_framework import permissions


class IsOwnerOrReadOnlyAsInstitute(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read (GET, HEAD, OPTIONS) permissions are allowed if either the user is the creator of the object, or belongs to the same
        # institute as the creator. Institute of course cannot be None!
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_institute_member(obj.institute) or request.user == obj.creator:
                return True
            return False
        # Write permissions are only allowed to the creator of the object.
        return obj.creator == request.user


