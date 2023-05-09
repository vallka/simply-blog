"""
WSGI config for simplyblog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv,dotenv_values

from django.core.wsgi import get_wsgi_application

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))

load_dotenv(env_path)

application = get_wsgi_application()
