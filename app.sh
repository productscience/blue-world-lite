#!/bin/bash

gunicorn blueworld.wsgi:application --preload --log-file - &
python manage.py rqworker default
