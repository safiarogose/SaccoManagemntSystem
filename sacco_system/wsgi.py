import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sacco_system.settings")

application = get_wsgi_application()

try:
    from .bootstrap import bootstrap_vercel_database

    bootstrap_vercel_database()
except Exception as exc:
    if os.environ.get("VERCEL"):
        print(f"Vercel database bootstrap failed: {exc}")
