"""
WSGI config for WeatherMapAPI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WeatherMapAPI.settings')

application = get_wsgi_application() 

# postgresql://weathermap_user:hWPbzIg6TYIwrehbkVIbpu5T7sSf3chz@dpg-da98s19srm7s73bipta0-a/weathermap_hsq6

# super user 
# username :richa
# password : test@123
# email : richa@gmail.com