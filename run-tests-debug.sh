#!/bin/bash

echo "Setting up Python environment and config ..."
. .ve3/bin/activate
. .env.sh
echo "done."

echo "Stopping lathermail ..."
pkill -f "ython lathermail.db"
echo "done."

echo "Deleting lathermail ..."
rm lathermail.db
echo "done."

echo "Resetting Django database ..."
. load.sh
echo "done ..."

echo "Starting the servers in the background ..."
python manage.py runserver > log_lathermail.txt 2>&1 &
lathermail --db-uri sqlite:////$PWD/lathermail.db > log_runserver.txt 2>&1 &
sleep 1
echo "done."

echo "Running tests ..."
python billing_week.py && behave "$@" || echo '++++++++++++++++++++++++++ FAILED ++++++++++++++++++++++++'
echo "done"

echo "Stopping lathermail ..."
pkill -f "ython lathermail.db"
echo "done."

echo "Deleting lathermail ..."
rm lathermail.db
echo "done."
