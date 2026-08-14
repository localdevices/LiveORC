from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that accepts 'email' and 'password' instead of 'username' and 'password'.
    This works with the custom CaseInsensitiveEmailBackend that uses email as USERNAME_FIELD.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace the 'username' field with an 'email' field
        self.fields.pop('username', None)
        from rest_framework import serializers
        self.fields['email'] = serializers.CharField()
    
    def validate(self, attrs):
        # Pass email as username to the parent authenticate method
        attrs['username'] = attrs['email']
        return super().validate(attrs)