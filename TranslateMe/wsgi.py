"""
WSGI config for TranslateMe project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
import os
import sys
import site
from django.core.wsgi import get_wsgi_application

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/theo/TranslateMe/myvenv/lib/python3.5/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/theo/TranslateMe')
sys.path.append('/home/theo/TranslateMe/TranslateMe')

os.environ['DJANGO_SETTINGS_MODULE'] = 'TranslateMe.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/home/theo/TranslateMe/myvenv/bin/activate_this.py")
exec(compile(open(activate_env, "rb").read(), activate_env, 'exec'), dict(__file__=activate_env))
application = get_wsgi_application()
