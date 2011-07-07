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

def apply_tag(tagger, target, tag, weight):
  tagset = TagSet(tagger=tagger, target=target)
  tagset.save()
  tag = Tag(name=tag, confidence=weight, tagset=tagset)
  tag.save()
