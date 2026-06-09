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

Username: safia
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
- Vercel auto-migration is enabled by default through `VERCEL_AUTO_MIGRATE=True` so fresh `/tmp` SQLite deployments do not crash with missing tables. If a fresh database has no users, the system creates the documented demo admin login `admin / admin123`; set `VERCEL_ADMIN_USERNAME` and `VERCEL_ADMIN_PASSWORD` to override it, then change the password before real use.
- Set `VERCEL_SEED_DEMO=True` on Vercel if you want the full demo records and the `safia / admin123` demo login online. Without this, Safia may exist only as a local database user or member record, not as a Vercel login.
