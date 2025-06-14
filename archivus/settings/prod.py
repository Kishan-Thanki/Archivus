from .base import *
from .installed_apps import *
from .middleware import *
from .database import *
from .jwt import *
from .swagger import *

# --- Production Overrides ---
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["http://localhost"])

# --- CORS ---
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost"])

# --- REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
