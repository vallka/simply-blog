from . settings import *

SECRET_KEY = os.environ['SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dj',
        'USER': 'gellifique',
        'PASSWORD': os.environ['POLLS_DB_PASSWORD'],
        #'HOST': '127.0.0.1',
        #'HOST': '172.31.18.205',
        'HOST': '172.31.14.216',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'presta': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gellifique_new',
        'USER': 'gellifique',
        'PASSWORD': os.environ['POLLS_DB_PASSWORD'],
        #'HOST': '127.0.0.1',
        #'HOST': '172.31.18.205',
        'HOST': '172.31.14.216',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
}  

ALLOWED_HOSTS = ['*']

TEMPLATE_SKIN = 'gellifique'
MARKDOWNX_IMAGE_MAX_SIZE = { 'size': (610, 1500), 'quality': 80 }

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

#WHITENOISE_STATIC_PREFIX = '/static/'
#FORCE_SCRIPT_NAME = '/pyadmin734r04xdw'
#STATIC_URL = '%s%s' % (FORCE_SCRIPT_NAME, WHITENOISE_STATIC_PREFIX)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT') 
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

EMAIL_FROM_USER = "info@gellifique.co.uk"
EMAIL_BCC_TO = None


DEBUG = True


sentry_sdk.init(
    environment="prod",
    dsn="https://235ef220fc8e4f9793858eacb15a542d@o480612.ingest.sentry.io/5528028",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

sentry_sdk.utils.MAX_STRING_LENGTH = 2048

