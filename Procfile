release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py setup_production
web: gunicorn myproject.wsgi --log-file -
