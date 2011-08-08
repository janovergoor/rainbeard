import random, string
from django.db import models
from django.contrib.auth.models import User
from validators import *
import common

#
#
# Represents a user. there is a one-to-one correspondance between users and
# profiles.
#
#
class Profile(models.Model):

  # Magic entry to link this with django's internal user table
  user = models.OneToOneField(User)

  # Gets the active face
  def active_face(self):
    return Face.objects.get(profile=self, is_active=True)


#
#
# Face for a user who has registered with us. A user may have multiple
# separate faces if they wish to keep certain agents distinct from each
# other.
#
#
class Face(models.Model):

  # Identifier
  label = models.CharField(max_length=20)

  # Which user do we belong to?
  profile = models.ForeignKey(Profile)

  # Is this face active?
  is_active = models.BooleanField(default=False)

  # Activates this face, deactivating the currently active face
  def activate(self):

    # Already active? No-op.
    if self.is_active:
      return

    # There should be exactly one active face if we're calling activate.
    # get() will throw an exception if anything else is the case.
    old = Face.objects.get(profile=self.profile,is_active=True)

    # Swap
    old.is_active = False
    self.is_active = True

    # Save
    old.save()
    self.save()

#
#
# Represents an agent in the social graph. An agent is a node to which tags
# can be attached.
#
# We want to user the same structure for Agent and PendingClaim. Unfortunately,
# django only lets you do this type of inheritance if the superclass is abstract.
# So we declare it Abstract here and inherit it more or less verbatim in Agent.
#
#
class AbstractAgent(models.Model):

  # Username on the given service. For example, jane.doe for the user jane.doe
  # on Facebook, and jane.doe@gmail.com for said email address.
  handle = models.CharField(max_length=100,validators=[validate_handle])

  # Name of service where this handle originates.
  #
  # Current valid values are:
  #   * email
  #   * facebook
  service = models.CharField(max_length=20,validators=[validate_service])

  # Face that this agent belongs to. NULL until somebody claims this
  # agent as themselves.
  owner = models.ForeignKey(Face, null=True, default=None)

  # Options
  class Meta:
    abstract = True

class Agent(AbstractAgent):

  # Options
  class Meta:
    unique_together = (('handle', 'service'))

#
#
# Represents a pending claim to an agent by a face.
#
#
class PendingClaim(AbstractAgent):

  # Generates a unique confirmation key. The checking here for duplicates is,
  # statistically, pretty unnecessary. But this stuff isn't on the critical path,
  # so why not?
  def generate_ckey():
    while True:
      k = ''.join(random.choice(string.ascii_letters + string.digits)
                  for x in range(common.ckey_length))
      if PendingClaim.objects.filter(ckey=k).count() == 0:
        return k

  # Confirmation Key
  ckey = models.CharField(max_length=common.ckey_length, unique=True,
                          default=generate_ckey)

  # Multiple faces may try to claim the same agent, so the handle,service
  # pair isn't necessarily unique like it is for Agent. use a handle,service,claimer
  # tuple instead.
  class Meta:
    unique_together = (('handle', 'service', 'owner'))

#
#
# Confidant relationships.
#
# Confidants relationships are always bidirectional. Alice cannot receive
# information from Bob unless she's willing to share information with him
# too. However, each person may set the propagation coefficient on
# information flowing from the other. As such, we represent each confidant
# relationship as two separate objects, and maintain the invariant that they
# must exist in pairs.
#
# TODO: add validation for the above invariant
#
#
class ConfidantLink(models.Model):

  # The source and destination of a confidant link are both Face objects.
  src = models.ForeignKey(Face, related_name='confidant_out_links')
  dst = models.ForeignKey(Face, related_name='confidant_in_links')

  # Propagation coefficient - how much does information through this link
  # propagate?
  prop_coef = models.PositiveSmallIntegerField(validators=[validate_prop_coef])

#
#
# Set of tags placed on a face.
#
#
class TagSet(models.Model):

  # The tagger and target are both Face objects.
  tagger = models.ForeignKey(Face, related_name='tagsets_by')
  target = models.ForeignKey(Face, related_name='tagsets_for')

  class Meta:
    unique_together = (('tagger', 'target'))

#
#
# Tag given in a relation.
#
#
class Tag(models.Model):

  # Name of the tag
  name = models.SlugField(max_length=40)

  # Confidence given to the tag
  confidence = models.PositiveSmallIntegerField(validators=[validate_confidence])

  # TagSet this tag corresponds to
  tagset = models.ForeignKey(TagSet)
