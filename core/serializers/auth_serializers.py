from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class LoginSerializer(serializers.Serializer):
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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text=_("Password for the new user (min 8 characters).")
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_("Confirm the password.")
    )

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password',
            'password_confirm',
            'degree_level',
            'program',
            'enrollment_year',
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': False},
            'degree_level': {'required': False},
            'program': {'required': False},
            'enrollment_year': {'required': False},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": _("Passwords do not match.")})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": _("This email address is already registered.")})

        username = data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": _("This username is already taken.")})

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data['email'],
                username=validated_data.get('username'),
                password=password,
                degree_level=validated_data.get('degree_level'),
                program=validated_data.get('program'),
                enrollment_year=validated_data.get('enrollment_year'),
            )
        return user
