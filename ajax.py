"""Asynchronous data exchange module."""

from django.http import HttpResponse
from rainbeard.models import *
from django.utils import simplejson as json
import identity, tagging


# Handy decorator to make sure the user is logged in and do various
# checking. Accepts a set of the parameters the function expects.
class check_ajax(object):
  def __init__(self, paramset):
    self.paramset = paramset
  def __call__(self, f):

    def wrapped_f(*args):

      # Grab the request
      request = args[0]

      # Make sure that we're authenticated
      if not request.user.is_authenticated():
        raise Exception('Not logged in!')

      # Make sure that the request looks right
      if request.method != 'POST':
        raise Exception('Wrong kind of request!')

      # Make sure that we have the parameters we want
      if not self.paramset <= set(request.POST):
        raise Exception('Wrong ajax parameters!')

      # Make sure that the request validates
      validate_ajax_params(request.POST)

      # Call through
      return f(*args);

    return wrapped_f

@check_ajax(set(('handle', 'service')))
def get_givens(request):

  # Parameters
  handle = request.POST['handle']
  service = request.POST['service']

  # The tagger is the logged in user
  tagger = request.user.get_profile().active_face

  # The destination is given in the query. It should exist. If it doesn't,
  # someone made a bad request. Let it throw.
  target = identity.get_face(handle, service)

  # Do the lookup
  tags = tagging.get_tagset(tagger, target)

  # Send the response
  return HttpResponse(json.dumps({'tags': tags}))
