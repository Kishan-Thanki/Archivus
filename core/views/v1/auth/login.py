from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from django.db.utils import OperationalError

from core.mixins.response_mixins import APIResponseMixin
from core.serializers.auth_serializers import LoginSerializer
from core.services.auth_service import AuthService


class LoginView(APIView, APIResponseMixin):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        # 1. Validate request data through "LoginSerializer".
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response(
                errors=serializer.errors,
                message="Invalid input provided.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2. Access validated data.
            identifier = serializer.validated_data.get('identifier')
            password = serializer.validated_data['password']

            # 3. Authenticate the user via your AuthService
            user = AuthService.authenticate_user(
                request,
                identifier=identifier,
                password=password
            )

            # 4. Handle expected authentication failure (user not found, wrong password, inactive)
            if not user:
                return self.error_response(
                    message="Invalid credentials provided.",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            tokens = AuthService.generate_jwt_tokens(user)

            return self.success_response(
                data={
                    "user": {
                        "id": user.id,
                        "username": user.username if user.username else None,
                        "email": user.email
                    },
                    "tokens": tokens
                },
                message="Login successful",
                status_code=status.HTTP_200_OK
            )

        except OperationalError:
            return self.error_response(
                message="A server error occurred. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            print(f"An unexpected error occurred during login: {e}")
            return self.error_response(
                message="An unexpected server error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, *args, **kwargs):
        """
        Example GET method. (Login endpoints typically only have POST methods.)
        """
        return self.success_response(
            data={
                "message": "This is a GET request to the Login endpoint. Use POST for actual login.",
                "example_info": "This endpoint handles user authentication via POST request."
            },
            message="GET request processed successfully",
            status_code=status.HTTP_200_OK
        )
