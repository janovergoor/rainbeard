from rainbeard import account
from rainbeard.models import *
from django.contrib.auth.models import User
from django.test.client import Client

# Utility to generate and activate a user.
#
# Returns the User object for the created user
def make_user(name, password=None, email=None):
  if not password:
    password = name + 'pass'
  if not email:
    email = name + '@example.com'
  user = account.register_user(name, password, email, False)
  account.do_claim(PendingClaim.objects.get(claimer=user.get_profile()).ckey)
  return User.objects.get(username=name)

# Dumps the database in JSON format in an external file
# NB: is possibly obsolete and can be done in a nicer fashion
def dump_database():
  from os import system
  os.system("./manage.py dumpdata > dbcontent.json")
