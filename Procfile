web: gunicorn manage:app --workers $WEB_CONCURRENCY
init: python manage.py db init
upgrade: python manage.py db upgrade
migrate: python manage.py db migrate



