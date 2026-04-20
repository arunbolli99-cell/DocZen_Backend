"""
WSGI config for doczen_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

print("🟢 WSGI: Starting application initialization...")

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doczen_api.settings')

print("🟢 WSGI: Loading Django WSGI application...")
application = get_wsgi_application()
print("✅ WSGI: Application successfully loaded and ready.")
