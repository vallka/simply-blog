from . settings import *

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vallka',
        'USER': 'vallkadotcom',
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'localhost',
        'PORT': 3307,
        'OPTIONS': {'charset': 'utf8mb4'},
    },
}


DEBUG = True
INTERNAL_IPS = ['127.0.0.1']


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
