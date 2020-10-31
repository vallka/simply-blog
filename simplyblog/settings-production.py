from . settings import *

SECRET_KEY = os.environ['SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dj',
        'USER': 'dj',
        'PASSWORD': os.environ['POLLS_DB_PASSWORD'],
        'HOST': '127.0.0.1',
    },
    'presta': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gellifique',
        'USER': 'gellifique',
        'PASSWORD': os.environ['POLLS_DB_PASSWORD'],
        'HOST': '127.0.0.1',
    },
    'presta-testa': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gellifique_test',
        'USER': 'gel',
        'PASSWORD': os.environ['POLLS_DB_PASSWORD'],
        'HOST': '127.0.0.1',
    },
}  

ALLOWED_HOSTS = ['*']


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

#WHITENOISE_STATIC_PREFIX = '/static/'
#FORCE_SCRIPT_NAME = '/pyadmin734r04xdw'
#STATIC_URL = '%s%s' % (FORCE_SCRIPT_NAME, WHITENOISE_STATIC_PREFIX)

DEBUG = True

sentry_sdk.init(
    environment="prod",
    dsn="https://fa080f42ed784f2aa4ad19b97809f449@o360522.ingest.sentry.io/5499309",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
