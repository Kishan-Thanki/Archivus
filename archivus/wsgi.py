"""
WSGI config for archivus project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import environ

from pathlib import Path

from django.core.wsgi import get_wsgi_application

project_root_for_env = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(project_root_for_env / ".env")

DJANGO_ENV = env("DJANGO_ENV", default="prod")
print(f"🌐 WSGI - DJANGO_ENV loaded: {DJANGO_ENV}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'archivus.settings.{DJANGO_ENV}')

application = get_wsgi_application()
