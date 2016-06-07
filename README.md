# Blueworld Lite

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
CREATE USER "blueworld-lite" WITH PASSWORD 'blueworld-lite';
CREATE DATABASE "blueworld-lite";
GRANT ALL PRIVILEGES ON DATABASE "blueworld-lite" TO "blueworld-lite";
```

Set up environment variables:

```
export DJANGO_SETTINGS_MODULE='blueworld.settings'
export DATABASE_URL='postgres://blueworld-lite:blueworld-lite@localhost:5432/blueworld-lite'
export DEBUG='True'
export EMAIL_HOST_PASSWORD='xxx'
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
DATABASE_URL='postgres://blueworld-lite:blueworld-lite@localhost:5432/blueworld-lite'
DEBUG='True'
EMAIL_HOST_PASSWORD='xxx'
```

Now run like this:

```
heroku local
```

### Production


```
heroku apps:create blue-world-lite
```

Get the branch you want to deploy and push it:

```
git checkout <branch>
git push heroku HEAD:master
```

Then set up the production config by running:

```
heroku config:set DJANGO_SETTINGS_MODULE=blueworld.settings
heroku config:set DEBUG=False
heroku config:set DATABASE_URL=...
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
heroku drains:add syslog+tls://logs2.papertrailapp.com:49245 --app blue-world-lite
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

## Setting up `maildump`

Todo.

## Setting up Travis

Todo.

## Setting up PaperTrail

Todo.

## Dev and Test

```
pip install -r requirements/dev.txt
```
