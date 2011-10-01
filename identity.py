"""Identity management module."""

from models import *

# Gets the face corresponding to a (handle, service) tuple.
#
# If the face and agent do not yet exist and create=True is passed, they
# are created. Otherwise, Face.DoesNotExist is raised.
def get_face(handle, service, create=False):
    try:
        return get_agent(handle, service, create=create).owner
    except Agent.DoesNotExist:
        raise Face.DoesNotExist()

# Gets the agent corresponding to a (handle, service) tuple.
#
# If the face and agent do not yet exist and create=True is passed, they
# are created. Otherwise, Agent.DoesNotExist is raised.
def get_agent(handle, service, create=False):

    # If we're not creating, just do a get(). We want the exception if it's raised.
    if not create:
        return Agent.objects.get(handle=handle, service=service)

    # If we are creating, give django the option to make the structures.
    agent, created = Agent.objects.get_or_create(handle=handle, service=service)
    return agent
