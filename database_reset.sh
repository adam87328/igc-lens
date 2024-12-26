#!/bin/bash

# delete old
find . -path "*/importer/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/importer/migrations/*.pyc"  -delete
find . -path "*/frontend/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/frontend/migrations/*.pyc"  -delete
rm db.sqlite3

# make new
python manage.py makemigrations importer
python manage.py migrate

DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --noinput --username=admin --email=admin@example.com
