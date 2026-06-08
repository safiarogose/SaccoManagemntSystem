import os

from django.core.management import call_command


def env_bool(name, default=True):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


def bootstrap_vercel_database():
    if not os.environ.get("VERCEL") or not env_bool("VERCEL_BOOTSTRAP_DB", True):
        return

    call_command("migrate", interactive=False, verbosity=0)
    call_command("seed_demo", verbosity=0)

    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group

    admin_group, _ = Group.objects.get_or_create(name="Administrator")
    User = get_user_model()
    safia, _ = User.objects.get_or_create(
        username="safia",
        defaults={
            "first_name": "Rogose",
            "last_name": "Safia",
            "email": "safia@ppsw.local",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    safia.is_staff = True
    safia.is_superuser = True
    safia.is_active = True
    safia.set_password(os.environ.get("VERCEL_ADMIN_PASSWORD", "123"))
    safia.save()
    safia.groups.add(admin_group)
