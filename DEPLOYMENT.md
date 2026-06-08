# Deployment

## Local Production Check

```powershell
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py seed_demo
py manage.py collectstatic --noinput
$env:DJANGO_DEBUG="False"
$env:DJANGO_SECRET_KEY="replace-this-with-a-long-random-secret"
$env:DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
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
- Put HTTPS in front of the app before enabling `DJANGO_SECURE_SSL_REDIRECT=True`.
