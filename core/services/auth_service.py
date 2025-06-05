from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

User = get_user_model()

class AuthService:
    @staticmethod
    def authenticate_user(request, identifier, password):
        """
        Authenticates a user using their email address and password.
        Returns the User object if authentication is successful and active, None otherwise.
        """
        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            if user.is_active:
                return user
            else:
                return None
        return None

    @staticmethod
    def generate_jwt_tokens(user):
        """
        Generates refresh and access tokens for a given user.
        Returns a dictionary containing 'refresh' and 'access' token strings.
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def verify_jwt_token(token_string):
        """
        Verifies an Access Token string and returns the associated user if valid.
        Raises InvalidToken if the token is invalid or expired.
        """
        try:
            access_token = AccessToken(token_string)
            user_id = access_token.payload.get('user_id')
            if user_id:
                try:
                    return User.objects.get(id=user_id, is_active=True)
                except User.DoesNotExist:
                    raise InvalidToken("User does not exist or is inactive.")
            else:
                raise InvalidToken("Token has no user ID.")
        except TokenError as e:
            raise InvalidToken(f"Token is invalid or expired: {e}")

    @staticmethod
    def refresh_access_token(refresh_token_string):
        """
        Refreshes an access token using a valid refresh token.
        Returns a dictionary containing the new 'access' token and the (potentially rotated) 'refresh' token.
        Raises InvalidToken if the refresh token is invalid or blacklisted.
        """
        try:
            refresh = RefreshToken(refresh_token_string)
            new_access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)

            return {
                'access': new_access_token,
                'refresh': new_refresh_token,
            }
        except TokenError as e:
            raise InvalidToken(f"Refresh token is invalid or expired: {e}")

    @staticmethod
    def blacklist_jwt_tokens(refresh_token_string):
        """
        Blacklists a refresh token (and implicitly its associated access token)
        to prevent further use, typically during logout.
        Returns True on successful blacklisting, False otherwise.
        """
        try:
            refresh = RefreshToken(refresh_token_string)
            refresh.blacklist()
            return True
        except TokenError as e:
            print(f"TokenError during blacklisting: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error blacklisting token: {e}")
            return False

    @staticmethod
    def get_token_for_user(user):
        """
        A utility to quickly get a fresh set of tokens for a user,
        useful after registration or other user state changes.
        """
        return AuthService.generate_jwt_tokens(user)