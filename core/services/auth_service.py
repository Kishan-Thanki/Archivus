import logging
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from core.services.custom_tokens import BlacklistableAccessToken
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class AuthService:

    @staticmethod
    def authenticate_user(request, identifier: str, password: str):
        """
        Authenticate the user by email (identifier) and password.
        Returns User instance if successful, raises ValidationError otherwise.
        """
        user = authenticate(request, username=identifier, password=password)

        if user is None:
            return None

        if not user.is_active:
            raise ValidationError("Account is inactive. Please contact support.")

        if getattr(user, "is_banned", False):  # safe fallback if some users don’t have this field
            raise ValidationError("Your account has been banned. Contact administrator.")

        return user

    @staticmethod
    def generate_jwt_tokens(user):
        """
        Generate access and refresh JWT tokens for the user.
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    @staticmethod
    def blacklist_jwt_tokens(refresh_token_str, access_token_str=None):
        """
        Blacklist the given refresh token and optionally access token (for logout).
        """
        try:
            # Blacklist refresh token
            refresh_token = RefreshToken(refresh_token_str)
            refresh_token.blacklist()
            logger.info("Refresh token blacklisted successfully.")

            # Blacklist access token if provided
            if access_token_str:
                access_token = BlacklistableAccessToken(access_token_str)
                access_token.blacklist()
                logger.info("Access token blacklisted successfully.")
        except TokenError as e:
            logger.warning(f"Failed to blacklist token(s): {e}")
            raise

    @staticmethod
    def refresh_access_token(refresh_token_str):
        """
        Validate and return new access token from refresh token.
        """
        try:
            refresh_token = RefreshToken(refresh_token_str)
            return {
                'access': str(refresh_token.access_token),
                'refresh': str(refresh_token)
            }
        except TokenError as e:
            logger.warning(f"Invalid token during refresh: {e}")
            raise