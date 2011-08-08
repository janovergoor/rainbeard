from rainbeard import account
from rainbeard.models import *
from django.contrib.auth.models import User

# Utility to generate and activate a user.
#
# Returns the User object for the created user
def make_user(name):
  password = name + 'pass'
  email = name + '@example.com'
  user = account.register_user(name, password, email, False)
  account.do_claim(PendingClaim.objects.get(claimer=user.get_profile()).ckey)
  return User.objects.get(username=name)
