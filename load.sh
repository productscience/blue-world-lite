#!/bin/bash

. .ve3/bin/activate
. .env.sh

psql -c 'DROP DATABASE blueworld;'
psql -c 'CREATE DATABASE blueworld;'

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata data/user.json
python manage.py loaddata data/initial.json
