"""
ASGI config for meduserstore project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

# from django.core.asgi import get_asgi_application
import django
from channels.routing import get_default_application
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meduserstore.settings')

# application = get_asgi_application()
django.setup()
application = get_default_application()
