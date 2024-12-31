#!/bin/bash

# delete old
find . -path "*/importer/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/importer/migrations/*.pyc"  -delete
find . -path "*/frontend/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/frontend/migrations/*.pyc"  -delete
rm db.sqlite3

# run database migrations
python manage.py makemigrations importer
python manage.py makemigrations frontend
python manage.py migrate

# create superuser, is stored in DB, has been deleted
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --noinput --username=admin --email=admin@example.com