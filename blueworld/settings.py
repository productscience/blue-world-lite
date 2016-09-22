"""
Django settings for blueworld project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Do NOT enable time travel on production
# or users could go back in time and mess things up
TIME_TRAVEL = not str(os.environ.get('TIME_TRAVEL')).lower() == 'false'
if TIME_TRAVEL:
    # Must import this before the datetime module (and hence before Django)
    import freezegun
ALLOW_SKIP_CURRENT_WEEK = False
if TIME_TRAVEL and str(os.environ.get('ALLOW_SKIP_CURRENT_WEEK')).lower() == 'true':
    ALLOW_SKIP_CURRENT_WEEK = True


import dj_database_url


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yw$xz=xr#r4@pd+cw1vg6el%s%6vpls00ylg(u_p-)t2kpd%w='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ['DEBUG'].lower() == 'true'
FAKE_IMPORTED_EMAILS = os.environ['FAKE_IMPORTED_EMAILS'].lower() == 'true'

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    # The Django sites framework is required for allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Hijack
    'hijack',
    'compat',
    # RQ
    'django_rq',
    #  Our apps
    'join',
    'exports'
]



if DEBUG:
    INSTALLED_APPS.append('django_extensions')
    # INSTALLED_APPS.append('debug_toolbar')


RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379/0'),
        'DEFAULT_TIMEOUT': 500,
    },
}

# RQ_EXCEPTION_HANDLERS = ['path.to.my.handler'] # If you need custom exception handlers



# Sentry
if 'RAVEN_DSN' in os.environ:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

# For allauth
SITE_ID = 1
# Where admins are redirected to after hijacking a user
LOGIN_REDIRECT_URL = '/dashboard'
# Where users go to login if they access a page they aren't supposed to
LOGIN_URL = '/login'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # ="optional" # Mandatory?
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_REMEMBER = False

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = False

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_SIGNUP_FORM_CLASS = 'join.forms.SignupForm'
ACCOUNT_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_LOGOUT_REDIRECT_URL = '/logged-out'

# TODO: Discuss this one
ACCOUNT_LOGOUT_ON_GET = True

# For Hijack
# Where admins are redirected to after hijacking a user
HIJACK_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
HIJACK_BUTTON_TEMPLATE = 'hijack_admin/admin_button.html'
HIJACK_REGISTER_ADMIN = False
HIJACK_LOGOUT_REDIRECT_URL = '/admin/'
HIJACK_AUTHORIZE_STAFF = True


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'join.helper.ThreadLocals',
]

ROOT_URLCONF = 'blueworld.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['blueworld/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blueworld.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

db_from_env = dj_database_url.config()
DATABASES = {'default': {}}
DATABASES['default'].update(db_from_env)

FIXTURE_DIRS = [os.path.join(BASE_DIR, 'data')]

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Strange things happen in timezones that aren't UTC
TIME_ZONE = 'UTC'
USE_TZ = True

USE_I18N = True

USE_L10N = True
FORMAT_MODULE_PATH = [
    'formats',
]

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
    )

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'


AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)


EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
if EMAIL_PORT:
    EMAIL_PORT = int(EMAIL_PORT)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# Let's have the default being True
EMAIL_USE_TLS = not str(os.environ.get('EMAIL_USE_TLS')).lower() == 'false'
# We use TLS, not SSL, so this isn't needed
# EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
SERVER_EMAIL = os.environ['SERVER_EMAIL']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
if os.environ.get('ALLOWED_HOSTS'):
    ALLOWED_HOSTS += [host.strip()
                      for host in os.environ['ALLOWED_HOSTS'].split(',')]
ADMINS = []
if os.environ.get('ADMINS'):
    ADMINS += [('admin', email.strip()) for email in os.environ['ADMINS'].split(',')]
LEAVER_EMAIL_TO = ['vegscheme@growingcommunities.org']
if os.environ.get('LEAVER_EMAIL_TO'):
    LEAVER_EMAIL_TO += [email.strip() for email in os.environ['LEAVER_EMAIL_TO'].split(',')]
if not LEAVER_EMAIL_TO:
    LEAVER_EMAIL_TO = ADMINS

# This is the maxiumum amount of time a user could have selected a
# collection point which is inactivated before they create their user
# account. Set to 40 mins.
SESSION_COOKIE_AGE = 40 * 60

# Raven
if 'RAVEN_DSN' in os.environ:
    import raven
    # print(raven.fetch_git_sha(os.path.dirname(__file__)))
    RAVEN_CONFIG = {
        'dsn': os.environ['RAVEN_DSN'],
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        # 'release': raven.fetch_git_sha(os.path.dirname(__file__)),
    }


# Go Cardless
import gocardless_pro
# https://github.com/gocardless/gocardless-pro-python
# https://developer.gocardless.com/2015-07-06/#overview
# https://gocardless.com/blog/an-introduction-to-our-api/
# https://gocardless.com/blog/goingcardless-an-introduction-to-gocardless/
GOCARDLESS_ENVIRONMENT = os.environ.get(
    'GOCARDLESS_ENVIRONMENT',
    'none'
)
GOCARDLESS_WEBHOOK_SECRET=os.environ['GOCARDLESS_WEBHOOK_SECRET']
GOCARDLESS_ACCESS_TOKEN = os.environ['GOCARDLESS_ACCESS_TOKEN']
SKIP_GOCARDLESS = str(os.environ.get('SKIP_GOCARDLESS', 'true')).lower() == 'true'
GOCARDLESS_CLIENT = gocardless_pro.Client(
    access_token=GOCARDLESS_ACCESS_TOKEN,
    environment=GOCARDLESS_ENVIRONMENT,
)
# Also make sure the endpoint is set up like: https://.../gocardless-events-webhook

SMALL_FRUIT_BAG_NAME='Small fruit'

# XXX Warning - this overrides the admin template!
RQ_SHOW_ADMIN_LINK = True
