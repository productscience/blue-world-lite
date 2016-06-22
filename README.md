# Blueworld Lite

[![Build Status](https://travis-ci.org/productscience/blue-world-lite.svg)](https://travis-ci.org/productscience/blue-world-lite)
[![Requirements Status](https://requires.io/github/productscience/blue-world-lite/requirements.svg)](https://requires.io/github/productscience/blue-world-lite/requirements/)
[![License: Apache 2](https://img.shields.io/badge/license-Apache%202-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

This is a Django project that handles management and billing of a Growing
Commuinities veg box scheme. It handles user registration and self-service,
pickup list generation and billing.

The codebase exists as a different apps all found in the `apps` directory. Each app can be installed and tested on its own, or as part of the overall application.

* `blueworld` - the main codebase:
  * provides base templates and CSS assets
  * sets up the Django admin, users and permissions
  * sets up `django-hijack` to allow administrators to log in as different users
* `join` - uses `pickup`, `bags` and the user model from `blueworld` to handle registration using `django-allauth`
* `pickup` - administer pick up locations
* `bags` - administer bag types

The `features` directory contains a `behave` environment for testing the
product via a web browser using selenium.

## Local Install

### Dependencies

Set up a virtual environment and install run dependencies:

```
pyvenv-3.5 .ve3
. .ve3/bin/activate
pip install -r requirements.txt -r requirements/dev.txt -r requirements/test.txt
```

Note that you are also installing commands from `requirements/dev.txt` and
`requirements/test.txt`. These are required for local testing, but not
production deployment.

### Database

Set up a PostgreSQL database:

```
psql (9.5.2)
CREATE USER blueworld WITH PASSWORD 'blueworld';
CREATE DATABASE blueworld;
GRANT ALL PRIVILEGES ON DATABASE blueworld TO blueworld;
```

To delete and re-create the database for testing you can run:

```
psql (9.5.2)
DROP DATABASE blueworld;
CREATE DATABASE blueworld;
GRANT ALL PRIVILEGES ON DATABASE blueworld TO blueworld;
```

### Configuration

Configuration is handled via environment variables, and how you set them up
depends on where you are deploying.

Here are the environment variables used and some example values:

```
DJANGO_SETTINGS_MODULE='blueworld.settings'
DATABASE_URL='postgres://blueworld:blueworld@localhost:5432/blueworld'
DEBUG='True'
SERVER_EMAIL='error@blueworld.example.com'
ADMINS='send-errors-here@example.com'
# Local
EMAIL_HOST='localhost'
EMAIL_HOST_USER='username'
EMAIL_HOST_PASSWORD='password'
EMAIL_PORT=2525
EMAIL_USE_TLS='False'
DEFAULT_FROM_EMAIL='no-reply@blueworld.example.com'
ALLOWED_HOSTS='localhost, 127.0.0.1'
```

For local development it is recommended you create a file called `.env.sh`
which has them all written out like this:

```
export CONFIG_OPTION='value'
```

Then you can activate all the config options each time you start a new terminal
window like this:

```
.env.sh
```

### Django

Make sure your environment is activates and configuration set:

```
. .ve3/bin/activate
.env.sh
```

Then once the environment variables are set up you can set up Django like this.

```
python manage.py makemigrations
python manage.py migrate
```

You can automate the setup of a super user and naming of the site with these
bash commands that use the Djano shell, and the environment variables you've
configured. (These are the commands used by Travis for example):

```
echo "from django.contrib.auth.models import User; User.objects.create_superuser('superuser', 'james@example.com', '123123ab')" | python manage.py shell
echo "from django.contrib.sites.models import Site; s = Site.objects.get(id=1); s.domain='localhost'; s.name='BlueWorld'; s.save()" | python manage.py shell
```

It is a good idea to keep the password and name set above, because they are
used in the tests.


### Data Migrations

#### Export Existing Data

You can export PostgreSQL data from another database by setting
`PATH_TO_VAGRANT_DIR` to be the path of the VM running the PostgreSQL instance
to migrate from and then running a `migrate.sh` script like this:

```
#!/bin/bash

set -e

CUR_DIR=$PWD
mkdir -p $CUR_DIR/data

pushd $PATH_TO_VAGRANT_DIR
echo "Migrating bag type ..."
vagrant ssh -c "sudo -u postgres psql grocom -c \"COPY (select name,active,\\\"order\\\",round((price*12)/52, 2) as weekly_cost from joinforms_bagtype where group_id=1) to '/tmp/bag_type.csv' with csv\"";
vagrant ssh -c "cat /tmp/bag_type.csv" > $CUR_DIR/data/bag_type.csv
echo "done."

echo "Migrating collection points ..."
vagrant ssh -c "sudo -u postgres psql grocom -c \"COPY (select name,\\\"where\\\",latitude,longitude,available,display_order from joinforms_pickuppoint where group_id=1) to '/tmp/collection_point.csv' with CSV\"";
vagrant ssh -c "cat /tmp/collection_point.csv" > $CUR_DIR/data/collection_point.csv
echo "done."
popd
```

You'll end up with a set of `.csv` files in the `data` directory. You can adjust them as you like.

#### Load Data

You can reset the database and load data from the `data` directory you've created with a script like this:

```
#!/bin/bash

psql -c 'DROP DATABASE blueworld;'
psql -c 'CREATE DATABASE blueworld;'
psql -c 'GRANT ALL PRIVILEGES ON DATABASE blueworld TO blueworld;'
python manage.py makemigrations
python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('superuser', 'james@example.com', '123123ab')" | python manage.py shell
echo "from django.contrib.sites.models import Site; s = Site.objects.get(id=1); s.domain='localhost'; s.name='BlueWorld'; s.save()" | python manage.py shell

psql blueworld -c "COPY join_bagtype(name,active,display_order,weekly_cost) from '$PWD/data/bag_type.csv' with csv;"
psql blueworld -c "COPY join_collectionpoint(name,location,latitude,longitude,active,display_order) from '$PWD/data/collection_point.csv' with csv"
```

## Running Locally

### Run the server

You'll need three terminals in order to develop BlueWorld Lite. One for the
development web sever, one for the development mail server, one to run the
tests.

In each terminal you'll need to activate your environment and make sure the
settings are set:

```
. .ve3/bin/activate
.env.sh
```

In the first terminal start the webserver:

```
python manage.py runserver
```

### Setting up `lathermail`

In order to check mail sending behaviour is correct you'll need a development
mailserver. We're using lathermail.

In the second terminal, activate the environment and check the settings are set:

```
. .ve3/bin/activate
.env.sh
```

Then run this to start the SMTP server:

```
lathermail --db-uri sqlite:////$PWD/lathermail.db
```

If the `lathermail` command isn't found it is probably because you didn't install all the requirements earlier. Try again now:

```
pip install -r requirements.txt -r requirements/dev.txt -r requirements/test.txt
```

Any time you want to run the tests, delete the `lathermail.db` file and restart
the server.

Lathermail has a concept of different inboxes based on SMTP logins. We set an
`EMAIL_USERNAME` and `EMAIL_PASSWORD` in the email configuration so lathermail
sets up an inbox with these credentials when receives the first mail.

Now any emails sent from Django will appear in the web interface at http://127.0.0.1:5000. 

To use the API you need to set some headers for the inbox you are after like
this. Make sure you specify the password configured in your email settings:

```
$ curl -0 -H "X-Mail-Password: password" http://127.0.0.1:5000/api/0/inboxes/
{
    "inbox_list": [
        "user"
    ],
    "inbox_count": 1
}
$ curl -0 -H "X-Mail-Password: password" http://127.0.0.1:5000/api/0/messages/
{
    "message_count": 1,
    "message_list": [
        {
            "recipients": [
                {
                    "address": "james@jimmyg.org",
                    "name": ""
                }
            ],
            "read": true,
            "recipients_raw": "james@jimmyg.org",
            "created_at": "2016-06-09T10:32:29.489615+00:00",
            "sender": {
                "address": "no-reply@blueworld.example.com",
                "name": ""
            },
            "subject": "[example.com] Please Confirm Your E-mail Address",
            "inbox": "user",
            "sender_raw": "no-reply@blueworld.example.com",
            "password": "password",
            "message_raw": ...
            "parts": [
                {
                    "type": "text/plain",
                    "size": 337,
                    "filename": null,
                    "charset": "utf-8",
                    "index": 0,
                    "is_attachment": false,
                    "body": ...
                }
            ],
            "_id": "0c110b02-ac30-4d1a-b181-27f6f9526f23"
        }
    ]
}
$ curl -0 -H "X-Mail-Password: password" http://127.0.0.1:5000/api/0/messages/0c110b02-ac30-4d1a-b181-27f6f9526f23
... Same content as the message above ...
```

You can also get attachments, and delete messages. See https://github.com/reclosedev/lathermail.


### Running the tests

In the third terminal, activate the environment and check the settings are set:

```
. .ve3/bin/activate
.env.sh
```

Make sure you have PhantomJS installed and the `phantomjs` command on your `PATH`.

Then run this command to run the tests:

```
behave
```

You'll need to reset the DB and lathermail on each test run. 

If you prefer not to do this manually in the three terminals, on Mac OS a
script like this can help, as long as you aren't running other similar
processes that might be accidentally killed.

This script also loads the `load.sh` script described above to reset the database:

```
#!/bin/bash

echo "Setting up Python environment and config ..."
. .ve3/bin/activate
. .env.sh
echo "done."

echo "Stopping lathermail ..."
pkill -f ython lathermail.db
echo "done."

echo "Stopping Django ..."
pkill -f ython manage.py runserver
echo "done"

echo "Stopping lathermail ..."
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
behave "$@" || echo "++++++++++++++++++++++++++++++ FAILED ++++++++++++++++++++++++++++++++"
echo "done"

echo "Stopping lathermail ..."
pkill -f ython lathermail.db
echo "done."

echo "Stopping Django ..."
pkill -f ython manage.py runserver
echo "done"

echo "Suceess"
```

If you just pass this script specific feature file paths, it will just run them.

## Travis

There is a `.travis.yml` file in the repo that performs similar steps to the
local install above. It will set up a running Django server and a Lathermail
instance. All you need to do is set up the config options using the Travis web
interface. `DEBUG` should be set to `False` for Travis testing.

If you plan to use Travis, I highly recommend you download version 1.9.7 and
use that for local testing, since that's the version Travis uses and you don't
want to be trying to track down differences with the Travis build.

On Mac OS X with phantom in the root of the directory, you can put the specific
version in your path like this:

```
export PATH=$PWD/phantomjs-1.9.7-macosx/bin/:$PATH
```

If you are using `.env.sh`, you might like to put the line above in there.

## Heroku

You can create a Heroku app like this:

```
heroku apps:create blueworld
```

To deploy to Heroku you'll need to set up the config options in Heroku's web
interface. Alternatively you can set them on the command line like this:

```
heroku config:set DJANGO_SETTINGS_MODULE=blueworld.settings
...
```

You'll need to set all the same environment variables as you did for the local
install and for Travis above, but make sure `DEBUG` is set to `False` for
Heroku.

To avoid having to check static assets into the repo, the templates are set up
to access files from an external URL. You'll have to change the templates to
reflect your own URI.

Use this command to deploy a particular branch:

```
git checkout <branch>
git push heroku HEAD:master
```

Once your app is pushed you'll need to run:

```
$ heroku run python manage.py migrate
```

You should be able to see your app at the correct domain now.

If you forget the name of your app:

```
heroku apps:list
```

### Setting up SendGrid on Heroku

Heroku offers a sendgrid starter addon that sets up a SendGrid account for you
and uses the API to send email. It requires a credit card to be added. You
don't need the add-on, it is easier to sign up for a SendGrid account and use
it directly.

Once you've created your account you can set up new credentials so that you
don't have to use your main username and password.

You'll need to set the `EMAIL_*` options to SendGrid ones:

```
EMAIL_HOST='smtp.sendgrid.net'
EMAIL_HOST_USER='sendgrid_username'
EMAIL_HOST_PASSWORD='sendgrid_password'
EMAIL_PORT=587
EMAIL_USE_TLS='True'
DEFAULT_FROM_EMAIL='no-reply@blueworld.example.com'
SERVER_EMAIL='error@blueworld.example.com'
ADMINS='send-errors-here@example.com'
```

### Setting up PaperTrail on Heroku

```
heroku drains:add syslog+tls://logs2.papertrailapp.com:<YOURPORT> --app blueworld`
```

### Setting up Sentry on Heroku

Send a test command like this:

```
python manage.py raven test
```

Set the DSN like this:

```
export RAVEN_DSN='...'
```
### Internationalisation

```
$ mkdir locale
$ PATH=/usr/local/Cellar/gettext/0.19.7/bin/:$PATH python manage.py makemessages -l en
```

Edit `django.po`. Then:

```
$ PATH=/usr/local/Cellar/gettext/0.19.7/bin/:$PATH python manage.py compilemessages
```
