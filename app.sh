#!/bin/bash

gunicorn blueworld.wsgi:application --preload --log-file - &
python worker.py
