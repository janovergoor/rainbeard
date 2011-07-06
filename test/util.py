"""Utility module for Rainbeard unit tests."""

from django.contrib.auth.models import User
from django.test.client import Client

from rainbeard import account
from rainbeard.models import *


def make_user(name, password=None, email=None):
    """
    Utility to generate and activate a user.

    Returns the User object for the created user.
    """
    if not password:
        password = name + 'pass'
    if not email:
        email = name + '@example.com'
    user = account.register_user(name, password, email, False)
    account.do_claim(PendingClaim.objects.get(claimer=user.get_profile()).ckey)
    return User.objects.get(username=name)


def dump_database():
    """
    Dumps the database in JSON format in an external file.
    """
    from os import system
    os.system("./manage.py dumpdata > dbcontent.json")
