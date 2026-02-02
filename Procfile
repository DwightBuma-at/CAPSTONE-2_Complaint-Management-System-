release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn myproject.wsgi --log-file -
