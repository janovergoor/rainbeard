from django.http import HttpResponse
from rainbeard.models import *
from django.utils import simplejson as json

#
# Handle asynchronous data exchange
#


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
        return HttpResponse('Not logged in!')

      # Make sure that the request looks right
      if not request.is_ajax() or request.method != 'POST':
        return HttpResponse('Wrong kind of request!')

      # Make sure that we have the parameters we want
      if not this.paramset <= request.POST:
        return HttResponse(json.dump({'error': 'Wrong ajax parameters!'}))

      # Make sure that the request validates
      try:
        validate_ajax_params(request.POST)
      except ValidationError:
        return HttResponse(json.dump({'error': 'Ajax parameters failed to validate!'}))

      # Call through
      self.f();

    return wrapped_f

@check_ajax(set(('handle', 'service')))
def get_givens(request):

  # Parameters
  handle = request.POST['handle']
  services = request.POST['service']

  # The source is the logged in user
  source = request.user.get_profile().active_profile

  # The destination is given in the query
  try:
    dest = Agent.objects.get(handle=handle,service=service)
  except Agent.DoesNotExist:
    return HttpResponse(json.dump({'tags': {}}))

  # Get our connection
  try:
    connections = Connection.objects.get(src=source,dst=dest)
  except Connection.DoesNotExist:
    return HttResponse(json.dump({'tags': {}}))

  # Get all the tags
  tags = Tag.objects.filter(connection=connection).values(['name', 'confidence'])

  # Send the response
  return HttpResponse(json.dump({'tags': tags}))
