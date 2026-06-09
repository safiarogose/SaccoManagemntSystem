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
- Set `DATABASE_URL` to a persistent Postgres database for live work. Vercel's `/tmp` SQLite database is temporary and can lose records after redeploys or cold starts.
- Run `py manage.py collectstatic --noinput` and serve `staticfiles/` from the web server.
- Use a production database for multi-user real deployment. SQLite is acceptable only for small local/internal testing.
- Put HTTPS in front of the app. `DJANGO_SECURE_SSL_REDIRECT` defaults to `True` when `DJANGO_DEBUG=False`.
- Enable `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True` and `DJANGO_SECURE_HSTS_PRELOAD=True` only when every production subdomain is served through HTTPS.
- Vercel auto-migration is enabled by default through `VERCEL_AUTO_MIGRATE=True` so fresh `/tmp` SQLite deployments do not crash with missing tables. If a fresh database has no users, the system creates the documented demo admin login `admin / admin123`; set `VERCEL_ADMIN_USERNAME` and `VERCEL_ADMIN_PASSWORD` to override it, then change the password before real use.
- Vercel seeds the full demo dashboard by default through `VERCEL_SEED_DEMO=True`, including Products, Members, Accounts, Loans, Transactions, and the `safia / admin123` demo login. Set `VERCEL_SEED_DEMO=False` only if you intentionally want a blank live database.

## Vercel Ready-To-Work Setup

Create a Postgres database, then add these Vercel environment variables:

```text
DATABASE_URL=postgres://...
DJANGO_SECRET_KEY=replace-this-with-a-long-random-secret-at-least-50-characters
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.vercel.app,your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
VERCEL_AUTO_MIGRATE=True
VERCEL_SEED_DEMO=True
```

Redeploy after saving the variables. The first live startup will run migrations and seed the dashboard records. For real data entry after launch, keep `DATABASE_URL` set so Products, Members, Accounts, Loans, and Transactions persist.
