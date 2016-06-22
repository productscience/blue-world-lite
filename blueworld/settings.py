"""
Django settings for blueworld project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yw$xz=xr#r4@pd+cw1vg6el%s%6vpls00ylg(u_p-)t2kpd%w='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ['DEBUG'].lower() == 'true'

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # The Django sites framework is required for allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # include the providers you want to enable:
    # Hijack
    'hijack',
    'compat',
    'hijack_admin',
    # Our apps
    'join',
]

if DEBUG:
    INSTALLED_APPS.append('django_extensions')
# Sentry
if 'RAVEN_DSN' in os.environ:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

# For allauth
SITE_ID = 1
LOGIN_REDIRECT_URL = '/dashboard'  # Where admins are redirected to after hijacking a user
LOGIN_URL = '/login'  # Where users go to login if they access a page they aren't supposed to

ACCOUNT_EMAIL_REQUIRED = True
#ACCOUNT_AUTHENTICATION_METHOD = "username_email"
#ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory" #="optional" # Mandatory?
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
HIJACK_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL  # Where admins are redirected to after hijacking a user
HIJACK_LOGOUT_REDIRECT_URL = '/admin/auth/user/'
# Needed for hijack-admin to work (but maybe not a great idea?)
HIJACK_ALLOW_GET_REQUESTS = True


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

import dj_database_url
db_from_env = dj_database_url.config()
DATABASES = {'default': {}}
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

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
    ALLOWED_HOSTS += [host.strip() for host in os.environ['ALLOWED_HOSTS'].split(',')]
ADMINS = []
if os.environ.get('ADMINS'):
    ADMINS += [email.strip() for email in os.environ['ADMINS'].split(',')]


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
