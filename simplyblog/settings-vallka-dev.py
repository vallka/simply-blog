from . settings import *

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']

# Local PostgreSQL, the password comes from %APPDATA%\postgresql\pgpass.conf
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vallka',
        'USER': 'vallka',
        'HOST': 'localhost',
    },
}


DEBUG = True
INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.csrf.CsrfViewMiddleware'),
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# Dev only: anything from 127.0.0.1 becomes admin, never use it behind a proxy
MIDDLEWARE += ['simplyblog.autologin.AutoLoginMiddleware']


#sentry_sdk.init(
#    environment="vallka-dev",
#    dsn="https://235ef220fc8e4f9793858eacb15a542d@o480612.ingest.sentry.io/5957755",
#    integrations=[DjangoIntegration()],
#
#    # If you wish to associate users to errors (assuming you are using
#    # django.contrib.auth) you may enable sending PII data.
#    send_default_pii=True
#)
#
#sentry_sdk.utils.MAX_STRING_LENGTH = 2048
