#!/bin/bash

. .ve3/bin/activate
. .env.sh

psql -c 'DROP DATABASE blueworld;' || exit
psql -c 'CREATE DATABASE blueworld;'

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata data/user.json
python manage.py loaddata initial.json
python manage.py import_user data/real/active.customer.bagchoice.and.mandate.json
