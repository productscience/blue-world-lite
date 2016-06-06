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


For Heroku you must also run::

heroku config:set DJANGO_SETTINGS_MODULE=blueworld.settings
heroku config:set DEBUG=False
heroku config:set DATABASE_URL=...

Then run:

~~~
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
~~~
