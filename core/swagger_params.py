from drf_yasg import openapi

jwt_authorization_header = openapi.Parameter(
    name='Authorization',
    in_=openapi.IN_HEADER,
    description='JWT access token, format: Bearer <access_token>',
    type=openapi.TYPE_STRING,
    required=True,
)
