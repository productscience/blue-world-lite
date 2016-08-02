#!/bin/bash

#  # Using Chrome, completing GoCardless, set SKIP_GOCARDLESS=false
#  BROWSER=chrome TEST_DEBUG=true ./run-tests.sh --no-capture "$@"
#  # Using Chrome, skipping GoCardless set SKIP_GOCARDLESS=true
#  BROWSER=chrome TEST_DEBUG=true ./run-tests.sh --tags=-gocardless --no-capture "$@"
#  # Using PhantomJS, skipping (this is what Travis does) set SKIP_GOCARDLESS=true
#  BROWSER=phantomjs TEST_DEBUG=true ./run-tests.sh --tags=-chrome --no-capture "$@"

echo "Stopping Django ..."
pkill -f "ython manage.py runserver"
echo "done"

./run-tests-debug.sh  "$@"

echo "Stopping Django ..."
pkill -f "ython manage.py runserver"
echo "done"
