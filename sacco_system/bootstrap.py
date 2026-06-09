import os

from django.core.management import call_command


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


def bootstrap_vercel_database():
    if not os.environ.get("VERCEL") or not env_bool("VERCEL_AUTO_MIGRATE", True):
        return

    call_command("migrate", interactive=False, verbosity=0)

    if env_bool("VERCEL_SEED_DEMO"):
        call_command("seed_demo", verbosity=0)

    admin_username = os.environ.get("VERCEL_ADMIN_USERNAME", "").strip()
    admin_password = os.environ.get("VERCEL_ADMIN_PASSWORD", "")
    if not admin_username or not admin_password:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if User.objects.exists():
            return
        admin_username = "admin"
        admin_password = "admin123"

    if not admin_username or not admin_password:
        return

    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group

    admin_group, _ = Group.objects.get_or_create(name="Administrator")
    User = get_user_model()
    admin_user, _ = User.objects.get_or_create(
        username=admin_username,
        defaults={
            "email": os.environ.get("VERCEL_ADMIN_EMAIL", ""),
            "is_staff": True,
            "is_superuser": True,
        },
    )
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.set_password(admin_password)
    admin_user.save()
    admin_user.groups.add(admin_group)
