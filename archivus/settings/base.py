import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SUPABASE_PROJECT_URL=(str, None),
    SUPABASE_STORAGE_BUCKET_NAME=(str, None),
    AWS_ACCESS_KEY_ID=(str, None),
    AWS_SECRET_ACCESS_KEY=(str, None),
    SUPABASE_S3_REGION_NAME=(str, 'ap-south-1'),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

ROOT_URLCONF = 'archivus.urls'
WSGI_APPLICATION = 'archivus.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Auth
AUTH_USER_MODEL = 'core.User'

# Timezone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_test')
MEDIA_URL = '/media_test/'

# Supabase Storage Configuration (S3-compatible via django-storages)
SUPABASE_PROJECT_URL = env("SUPABASE_PROJECT_URL")
AWS_STORAGE_BUCKET_NAME = env("SUPABASE_STORAGE_BUCKET_NAME")
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = env("SUPABASE_S3_REGION_NAME", default='ap-south-1')

# Set django-storages as the default file storage backend
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Boto3 client specific configuration for custom S3 endpoints
# This is crucial for Supabase's S3 compatibility
AWS_S3_ENDPOINT_URL = f"{SUPABASE_PROJECT_URL}/storage/v1/s3" if SUPABASE_PROJECT_URL else None
AWS_S3_CUSTOM_DOMAIN = None # Typically None when using a custom endpoint URL like Supabase's
S3BOTO3_CLIENT_KWARGS = {'endpoint_url': AWS_S3_ENDPOINT_URL}
S3BOTO3_REGION_NAME = AWS_S3_REGION_NAME

# Recommended default ACL for uploaded files
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_FILE_OVERWRITE = False
