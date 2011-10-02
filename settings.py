"""
Settings module.

This module must be imported in the project-wide settings module in order for
rainbeard to work properly. Rainbeard is designed to be a system-within-
an-app, and so it requires control of certain site-wide django settings
(such as AUTH_PROFILE_MODULE) to function properly. However, much of the
other site-wide configuration varies from install to install, so it doesn't
make sense to distribute the whole site with rainbeard. As a compromise,
rainbeard requires that settings.py and url.py import configuration from
within the rainbeard app.

At the end of your project settings.py file, you should do:
from rainbeard.settings import *
"""

# Define the user profile model
AUTH_PROFILE_MODULE = 'rainbeard.Profile'

# Define the login URL
LOGIN_URL = '/login'
