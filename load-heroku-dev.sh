#!/bin/bash

set -e

confirm () {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [y/N]} " response
    case $response in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}

echo "Pushing HEAD to Heroku"
confirm || git push heroku HEAD:master

echo "Resetting $HEROKU_PG_NAME on $HEROKU_APP_NAME"
confirm || exit

# Need to stop the clock to free up a dyno
heroku ps:scale clock=0
heroku pg:reset $HEROKU_PG_NAME --confirm $HEROKU_APP_NAME
# python manage.py collectstatic --noinput
# python manage.py makemigrations
heroku run python manage.py migrate
heroku run python manage.py loaddata data/user.json
heroku run python manage.py loaddata initial.json

# import the pickup points
heroku run "aws s3 cp $AWS_BUCKET/$IMPORT_DATE/$PICKUP_POINTS $PICKUP_POINTS; ./manage.py loaddata $PICKUP_POINTS"
# import the customers
heroku run "aws s3 cp $AWS_BUCKET/$IMPORT_DATE/$CUSTOMERS $CUSTOMERS; ./manage.py loaddata $CUSTOMERS"

heroku ps:scale clock=1
echo "Success."
