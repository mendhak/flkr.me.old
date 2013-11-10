"""
WSGI config for flkrme project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/mendhak/flkr.me/venv/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/mendhak/flkr.me/')
sys.path.append('/home/mendhak/flkr.me/flkrme')

os.environ['DJANGO_SETTINGS_MODULE'] = 'flkrme.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/home/mendhak/flkr.me/venv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
