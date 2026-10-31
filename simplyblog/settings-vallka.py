from . settings import *

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# nginx terminates TLS, without this SECURE_SSL_REDIRECT loops
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
    },
}


DEBUG = False
INTERNAL_IPS = ['127.0.0.1','90.253.213.37','87.74.227.238','88.23.238.60']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'incremental': True,
    'root': {
        'level': 'DEBUG',
    },
}


from icecream import ic
ic.disable()

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    environment="prod",
    dsn="https://f1d4719a0ee74c7e98fed48ceacb1f58@o4504844591562753.ingest.sentry.io/4504844608405504",
    integrations=[
        DjangoIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
#sentry_sdk.utils.MAX_STRING_LENGTH = 2048
