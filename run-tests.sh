#!/bin/bash


echo "Stopping Django ..."
pkill -f "ython manage.py runserver"
echo "done"

./run-tests-debug.sh  "$@"

echo "Stopping Django ..."
pkill -f "ython manage.py runserver"
echo "done"
