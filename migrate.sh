#!/bin/bash
python manage.py makemigrations importer
python manage.py makemigrations frontend
python manage.py migrate