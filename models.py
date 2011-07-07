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

  # Gets the active face. Returns None if the user has no faces yet.
  def active_face(self):
    try:
      return Face.objects.get(owner=self, is_active=True)
    except Face.DoesNotExist:
      return None

#
#
# Faces represent distinct online identities. A user may have multiple
# separate faces if they wish to keep certain agents distinct from each
# other.
#
# Every Agent must correspond to a Face, but some Agents do not correspond
# (yet) to a user that has registered with us. So some Faces do not have an
# owner. We refer to these as 'unbound faces'.
#
#
class Face(models.Model):

  # Identifier
  label = models.CharField(max_length=20, blank=True)

  # Which user do we belong to? Null if we're unbound.
  owner = models.ForeignKey(Profile, null=True, blank=True, default=None)

  # Is this face active?
  is_active = models.BooleanField(default=False)

  # Activates this face, deactivating the currently active face. It is an error
  # to all this method on an unbound face.
  def activate(self):

    # Unbound? Error
    if owner is None:
      raise Exception('Calling activate() on unbound face!')

    # Already active? No-op.
    if self.is_active:
      return

    # There should be exactly one active face if we're calling activate.
    # get() will throw an exception if anything else is the case.
    old = Face.objects.get(owner=self.owner,is_active=True)

    # Swap
    old.is_active = False
    self.is_active = True

    # Save
    old.save()
    self.save()


class Agent(models.Model):

  # Username on the given service. For example, jane.doe for the user jane.doe
  # on Facebook, and jane.doe@gmail.com for said email address.
  handle = models.CharField(max_length=100,validators=[validate_handle])

  # Name of service where this handle originates.
  #
  # Current valid values are:
  #   * email
  #   * facebook
  service = models.CharField(max_length=20,validators=[validate_service])

  # Face that this agent belongs to.
  owner = models.ForeignKey(Face, default=lambda: Face.objects.create())

  # Options
  class Meta:
    unique_together = (('handle', 'service'))

#
#
# Represents a pending claim to a face by a user.
#
#
class PendingClaim(models.Model):

  # Claimer
  claimer = models.ForeignKey(Profile)

  # Face being claimed
  face = models.ForeignKey(Face)

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

  # Options
  class Meta:
    unique_together = (('claimer', 'face'))


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


#
#
# In-memory representation of the confidant network. Can be read as a 
# user x user matrix, where the (i,j)th value is the confidence that 
# user i has in user j. The value is 0 when there is no relation between
# them.
#
# NB: This implementation assumes that the user id are given out in 
# sequence and consist of integers, starting with 0.
# NB: This implementation optimizes the lookup of high confidant links
# but is less effective in terms of adding links and looking up specific links
#
#
class ConfidantNetwork(models.Model):
  
  # The network itself, start with empty first elemet
  network = [0]
  
  # Adds a link from src to dst with the given weight
  def add_link(self, src, dst, weight):
    # check if the user is already present in the confidant network  
    if len(self.network) > 1 and len(self.network) - 1 >= src:
      # find the location of the biggest link that is smaller than weight
      id = 0
      while (id < len(self.network[src])) and (weight < self.network[src][id][0]):
        id =+ 1
      self.network[src].insert(id,(weight,dst))
    # otherwise this is the first confidant link for this user
    else:
      self.network.append([(weight, dst)])

  # Returns the weight of the link if there is a confidence relation,
  # or 0 when there is none.
  def get_link(self, src, dst):
    # check if the src user is present in the network
    if len(self.network) >= src:
      # iterate over src'es links
      for link in self.network[src]:
        # return weight if dst is in src'es links
        if link[1] == dst:
          return link[0]
    # otherwise, if src is not present or dst is not in src'es link
    return 0
    
  # Returns an enumerator which containts the confidents of the input
  # user, ordered by the confidance that it has in them.
  def get_confidants(self, src):
    return self.network[src]  # TODO: should be an enumerator?

  # Prints out the confidant network
  def print_out(self):
    print "\nState of the network:"
    for x in range(1,len(self.network)):
      print x, ":", 
      for y in self.network[x]:
        print '(%d,%.2f)' % (y[1], y[0]), 
      print ""

