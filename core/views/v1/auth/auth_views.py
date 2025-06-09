import logging

from django.db.utils import OperationalError

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


from core.mixins.response_mixins import APIResponseMixin
from core.serializers.auth_serializers import RegisterSerializer, LoginSerializer
from core.services.auth_service import AuthService
from core.swagger_params import jwt_authorization_header


logger = logging.getLogger(__name__)

class RegisterView(APIView, APIResponseMixin):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response('Registration successful and user logged in.', RegisterSerializer),
            400: 'Invalid input for registration.',
            500: 'Server error during registration.',
        },
    )

    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Registration failed: {serializer.errors}")
            return self.error_response(
                errors=serializer.errors,
                message="Invalid input for registration.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = serializer.save()
            tokens = AuthService.generate_jwt_tokens(user)
            logger.info(f"User registered successfully: {user.email} (ID: {user.id})")
            return self.success_response(
                data={
                    "user": {
                        "id": user.id,
                        "username": user.username or None,
                        "email": user.email,
                        "points": getattr(user, "points", None),
                        "degree_level_id": user.degree_level.id if user.degree_level else None,
                        "program_id": user.program.id if user.program else None,
                        "enrollment_year": user.enrollment_year,
                    },
                    "tokens": tokens,
                },
                message="Registration successful and user logged in.",
                status_code=status.HTTP_201_CREATED,
            )
        except OperationalError:
            logger.exception("Database error during registration.")
            return self.error_response(
                message="Server error during registration. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.exception(f"Unexpected error during registration: {e}")
            return self.error_response(
                message="Unexpected server error during registration.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class LoginView(APIView, APIResponseMixin):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Login user and get JWT tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response('Login successful.', LoginSerializer),
            400: 'Invalid input provided.',
            401: 'Invalid credentials.',
            500: 'Server error.',
        },
    )

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                errors=serializer.errors,
                message="Invalid input provided.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            identifier = serializer.validated_data.get('identifier')
            password = serializer.validated_data['password']

            user = AuthService.authenticate_user(request, identifier, password)
            if not user:
                return self.error_response(
                    message="Invalid credentials.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            tokens = AuthService.generate_jwt_tokens(user)
            return self.success_response(
                data={
                    "user": {
                        "id": user.id,
                        "username": user.username or None,
                        "email": user.email,
                    },
                    "tokens": tokens,
                },
                message="Login successful.",
                status_code=status.HTTP_200_OK,
            )
        except OperationalError:
            return self.error_response(
                message="Server error. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.exception(f"Unexpected error during login: {e}")
            return self.error_response(
                message="Unexpected server error.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class LogoutView(APIView, APIResponseMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout user by blacklisting tokens.",
        manual_parameters=[jwt_authorization_header],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token string'),
            },
        ),
        responses={
            200: 'Successfully logged out.',
            400: 'Refresh token is required or invalid.',
            401: 'Unauthorized.',
            500: 'Unexpected server error during logout.',
        },
    )

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")
        access_token = request.headers.get("Authorization", "").split("Bearer ")[-1] if "Authorization" in request.headers else None

        if not refresh_token:
            logger.warning("Logout failed: no refresh token provided.")
            return self.error_response(
                message="Refresh token is required for logout.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            AuthService.blacklist_jwt_tokens(refresh_token, access_token)
            logger.info(f"User {request.user.id} logged out successfully.")
            return self.success_response(
                message="Successfully logged out.",
                status_code=status.HTTP_200_OK,
            )
        except TokenError as e:
            logger.warning(f"Logout failed: invalid or expired refresh token. {e}")
            return self.error_response(
                message="Invalid or expired refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception(f"Unexpected error during logout for user {request.user.id}. {e}")
            return self.error_response(
                message="Unexpected server error during logout.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class RefreshTokenView(APIView, APIResponseMixin):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Refresh access token using refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token string'),
            },
        ),
        responses={
            200: 'Access token refreshed.',
            400: 'Refresh token is required.',
            401: 'Invalid or expired refresh token.',
            500: 'Unexpected server error during token refresh.',
        },
    )

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return self.error_response(
                message="Refresh token is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            new_tokens = AuthService.refresh_access_token(refresh_token)
            return self.success_response(
                data=new_tokens,
                message="Access token refreshed.",
                status_code=status.HTTP_200_OK,
            )
        except (InvalidToken, TokenError) as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            logger.exception(f"Unexpected error during token refresh: {e}")
            return self.error_response(
                message="Unexpected server error during token refresh.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )