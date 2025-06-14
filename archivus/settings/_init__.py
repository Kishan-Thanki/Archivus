import os

ENV = os.getenv("DJANGO_ENV", "dev")
print(f"🌐 DJANGO_ENV loaded: {ENV}")

if ENV == "prod":
    from .prod import *
else:
    from .dev import *
