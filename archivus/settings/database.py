import dj_database_url
from .base import env

DATABASES = {
    'default': dj_database_url.parse(env("DATABASE_URL"))
}
