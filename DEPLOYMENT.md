# Deployment

## Local Production Check

```powershell
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py seed_demo
py manage.py collectstatic --noinput
$env:DJANGO_DEBUG="False"
$env:DJANGO_SECRET_KEY="replace-this-with-a-long-random-secret-at-least-50-characters"
$env:DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
$env:DJANGO_CSRF_TRUSTED_ORIGINS="https://your-domain.com"
$env:DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS="True"
$env:DJANGO_SECURE_HSTS_PRELOAD="True"
py manage.py check --deploy
py manage.py runserver
```

## Login

The demo seed creates:

```text
Username: admin
Password: admin123
```

Change this password before real use from Django admin or by creating a new superuser.

## Production Notes

- Set `DJANGO_SECRET_KEY` to a strong private value.
- Set `DJANGO_DEBUG=False`.
- Set `DJANGO_ALLOWED_HOSTS` to the deployed domain names.
- Set `DJANGO_CSRF_TRUSTED_ORIGINS` to the deployed HTTPS origins.
- Run `py manage.py collectstatic --noinput` and serve `staticfiles/` from the web server.
- Use a production database for multi-user real deployment. SQLite is acceptable only for small local/internal testing.
- Put HTTPS in front of the app. `DJANGO_SECURE_SSL_REDIRECT` defaults to `True` when `DJANGO_DEBUG=False`.
- Enable `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True` and `DJANGO_SECURE_HSTS_PRELOAD=True` only when every production subdomain is served through HTTPS.
- Vercel database bootstrapping is disabled by default. Set `VERCEL_BOOTSTRAP_DB=True` only when you intentionally want migrations to run at startup, and set `VERCEL_ADMIN_USERNAME` plus `VERCEL_ADMIN_PASSWORD` if an admin account should be created.
