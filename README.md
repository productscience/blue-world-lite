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

