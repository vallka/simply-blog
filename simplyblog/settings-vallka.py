from . settings import *

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']



DEBUG = True


sentry_sdk.init(
    environment="vallka",
    dsn="https://235ef220fc8e4f9793858eacb15a542d@o480612.ingest.sentry.io/5957755",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

sentry_sdk.utils.MAX_STRING_LENGTH = 2048
