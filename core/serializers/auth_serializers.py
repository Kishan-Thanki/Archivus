from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    """
    Serializer for validating login credentials.
    The 'identifier' field now explicitly accepts the user's email address for login.
    """
    identifier = serializers.CharField(
        write_only=True,
        help_text=_('Enter your email address.')
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Enter your password.')
    )

    def validate(self, data):
        """
        Custom validation method for the LoginSerializer.
        Ensures that both the 'email identifier' and 'password' fields are provided.
        """
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier:
            raise serializers.ValidationError(
                {'identifier': _('This field (email) is required.')},
                code='required_email_identifier'
            )

        if not password:
            raise serializers.ValidationError(
                {'password': _('This field is required.')},
                code='required_password'
            )
        return data