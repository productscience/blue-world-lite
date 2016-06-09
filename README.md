# Blueworld Lite

[![Build Status](https://travis-ci.org/productscience/blue-world-lite.svg)](https://travis-ci.org/productscience/blue-world-lite)
[![Requirements Status](https://requires.io/github/productscience/blue-world-lite/requirements.svg?branch=feature%2Fjoin)](https://requires.io/github/productscience/blue-world-lite/requirements/?branch=feature%2Fjoin)
[![License: Apache 2](https://img.shields.io/badge/license-Apache%202-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

This is a Django project that handles management and billing of a Growing
Commuinities veg box scheme. It handles user registration and self-service,
pickup list generation and billing.

The codebase exists as a different apps all found in the `apps` directory. Each app can be installed and tested on its own, or as part of the overall application.

* `blueworld` - the main codebase:
  * provides base templates and CSS assets
  * sets up the Django admin, users and permissions
  * sets up `django-hijack` to allow administrators to log in as different users
* `pickup` - administer pick up locations
* `bags` - administer bag types
* `join` - uses `pickup`, `bags` and the user model from `blueworld` to handle registration using `django-allauth`

The `features` directory contains a `behave` environment for testing the
product via a web browser using selenium.

Set up a database:

```
psql (9.5.2)
CREATE USER blueworld WITH PASSWORD 'blueworld';
CREATE DATABASE blueworld;
GRANT ALL PRIVILEGES ON DATABASE blueworld TO blueworld;
```

Set up environment variables:

```
export DJANGO_SETTINGS_MODULE='blueworld.settings'
export DATABASE_URL='postgres://blueworld:blueworld@localhost:5432/blueworld'
export DEBUG='True'
export EMAIL_HOST='smtp.sendgrid.net'
export EMAIL_HOST_USER='blue-world-lite'
export EMAIL_HOST_PASSWORD='xxx'
export EMAIL_PORT=587
export EMAIL_USE_TLS='True'
export DEFAULT_FROM_EMAIL='no-reply@blueworld.example.com'
export SERVER_EMAIL='error@blueworld.example.com'
```

Set up a virtual environment and install run dependencies:

```
pyvenv-3.5 .ve3
. .ve3/bin/activate
pip install -r requirements.txt
```

Set up Django:

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Run the server:

```
python manage.py runserver
```


## Heroku

### Local

Make sure you have the Heroku toolbelt installed then create a `.env` file with all the environment variables from earlier (without the `export` in front):

```
DJANGO_SETTINGS_MODULE='blueworld.settings'
DATABASE_URL='postgres://blueworld:blueworld@localhost:5432/blueworld'
DEBUG='True'
EMAIL_HOST='smtp.sendgrid.net'
EMAIL_HOST_USER='blue-world-lite'
EMAIL_HOST_PASSWORD='xxx'
EMAIL_PORT=587
EMAIL_USE_TLS='True'
DEFAULT_FROM_EMAIL='no-reply@blueworld.example.com'
SERVER_EMAIL='error@blueworld.example.com'
```

Now run like this:

```
heroku local
```

### Production


```
heroku apps:create blueworld
```

Get the branch you want to deploy and push it:

```
git checkout <branch>
git push heroku HEAD:master
```

Then set up the production config by running similar commands for each of the settings in `.env`. e.g.:

```
heroku config:set DJANGO_SETTINGS_MODULE=blueworld.settings
heroku config:set DEBUG=False
heroku config:set DATABASE_URL=...
... 
```

Then run:

```
$ heroku run python manage.py migrate
Running python manage.py migrate on ⬢ gentle-citadel-81843... up, run.3758
Operations to perform:
  Apply all migrations: contenttypes, auth, sessions, admin
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying sessions.0001_initial... OK
$  heroku run python manage.py createsuperuser
Running python manage.py createsuperuser on ⬢ gentle-citadel-81843... up, run.4591
Username (leave blank to use 'u37612'): thejimmyg
Email address: james@3aims.com
Password:
Password (again):
Superuser created successfully.
```

You should be able to see your app at the correct domain now.

After loging into the admin at `/admin`, change the site name from example.com to whatever
you like. This will be used in the emails sent by the registration system.

If you forget the name of your app:

```
heroku apps:list
```

#### Setting up logging

```
heroku drains:add syslog+tls://logs2.papertrailapp.com:49245 --app blueworld
```

# Setting up SendGrid

Heroku offers a sendgrid starter addon that sets up a SendGrid account for you
and uses the API to send email. It requires a credit card to be added. You
don't need the add-on, it is easier to sign up for a SendGrid account and use
it directly.

Once you've created your account you can set up new credentials so that you
don't have to use your main username and password.

You'll need to add the following settings to your `.env`, `.env.sh` and
production configs:

```
EMAIL_HOST='smtp.sendgrid.net'
EMAIL_HOST_USER='sendgrid_username'
EMAIL_HOST_PASSWORD='sendgrid_password'
EMAIL_PORT=587
EMAIL_USE_TLS='True'
DEFAULT_FROM_EMAIL='no-reply@blueworld.example.com'
SERVER_EMAIL='error@blueworld.example.com'
```

```
heroku config:set EMAIL_HOST='smtp.sendgrid.net'
heroku config:set EMAIL_HOST_USER='user_password'
heroku config:set EMAIL_HOST_PASSWORD='smtp_password'
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS='True'
heroku config:set DEFAULT_FROM_EMAIL='no-reply@blueworld.example.com'
heroku config:set SERVER_EMAIL='error@blueworld.example.com'
```

```
export EMAIL_HOST='smtp.sendgrid.net'
export EMAIL_HOST_USER='user_password'
export EMAIL_HOST_PASSWORD='smtp_password'
export EMAIL_PORT=587
export EMAIL_USE_TLS='True'
export DEFAULT_FROM_EMAIL='no-reply@blueworld.example.com'
export SERVER_EMAIL='error@blueworld.example.com'
```

## Setting up `lathermail`

```
lathermail --db-uri sqlite:////$D/lathermail.db
```

Set up Django by setting these environment variables and restarting the server:

```
export EMAIL_HOST='localhost'
export EMAIL_HOST_USER='user'
export EMAIL_HOST_PASSWORD='password'
export EMAIL_PORT=2525
export EMAIL_USE_TLS='False'
export DEFAULT_FROM_EMAIL='no-reply@blueworld.example.com'
export SERVER_EMAIL='error@blueworld.example.com'
```

Latermail has a concept of different inboxes based on SMTP logins. Above we used `user` and `password` so lathermail sets up an inbox with these when it receives the first mail.

Now emails sent from Django will appear in the web interface at http://127.0.0.1:5000. 

To use the API you need to set some headers for the inbox you are after like this:

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

With the config described above, the data is stored in an SQLite database too.

## Setting up Travis

You need to configure the following environment variables in the Travis interface:

* `DJANGO_SETTINGS_MODULE` blueworld.settings
* `DATABASE_URL` postgres://blueworld:blueworld@localhost:5432/blueworld
* `DEBUG` False
* `DEFAULT_FROM_EMAIL` no-reply@blueworld.example.com
* `SERVER_EMAIL` error@blueworld.example.com
* `ALLOWED_HOSTS` localhost, 127.0.0.1


## Setting up PaperTrail

```
heroku drains:add syslog+tls://logs2.papertrailapp.com:<YOURPORT> --app blueworld`
```

## Dev and Test

```
pip install -r requirements.txt -r requirements/dev.txt -r requirements/test.txt
```
