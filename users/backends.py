"""Authentication with case-insensitive email addresses."""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CaseInsensitiveEmailBackend(ModelBackend):
    """
    Authenticates against email field, case-insensitive.
    Existing passwords remain valid since we only change the username lookup.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Normalize email to lowercase for lookup
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            return None
        
        # Check password (unchanged, works with existing hashes)
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None