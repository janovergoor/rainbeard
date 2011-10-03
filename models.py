"""
SQL-backed data model module.

This module is used by Django to map various data storage backends to python
objects.
"""
import random
import string

from django.db import models
from django.contrib.auth.models import User

import common
from validators import *


class Profile(models.Model):
    """
    Profile data model.

    In Django, the User table itself is immutable, so the framework provides
    the ability to associate a 'profile' with a user account for application-
    specific data. There is a one-to-one correspondance between users and
    profiles.
    """

    # Magic entry to link this with django's internal user table
    user = models.OneToOneField(User)

    def active_face(self):
        """
        Gets the active face.

        Returns None if the user has no faces yet.
        """

        try:
            return Face.objects.get(owner=self, is_active=True)
        except Face.DoesNotExist:
            return None


class Face(models.Model):
    """
    Face data model.

    Faces represent distinct online identities. A user may have multiple
    separate faces if they wish to keep certain agents distinct from each
    other.

    Every Agent must correspond to a Face, but some Agents do not correspond
    (yet) to a user that has registered with us. So some Faces do not have an
    owner. We refer to these as 'unbound faces'.
    """

    # Identifier
    label = models.CharField(max_length=20, blank=True)

    # Which user do we belong to? Null if we're unbound.
    owner = models.ForeignKey(Profile, null=True, blank=True, default=None)

    # Is this face active?
    is_active = models.BooleanField(default=False)

    def activate(self):
        """
        Activates this face, deactivating the currently active face.

        It is an error to call this method on an unbound face.
        """

        # Unbound? Error
        if owner is None:
            raise Exception("Calling activate() on unbound face!")

        # Already active? No-op.
        if self.is_active:
            return

        # There should be exactly one active face if we're calling activate.
        # get() will throw an exception if anything else is the case.
        old = Face.objects.get(owner=self.owner, is_active=True)

        # Swap.
        old.is_active = False
        self.is_active = True

        # Save.
        old.save()
        self.save()


class Agent(models.Model):
    """
    Agent data model.

    Agents represent 'user accounts' on the various web services that Rainbeard
    supports. Agents are represented as (handle, service) tuples, such as
    ('alice@example.com', 'email') and ('bob.baz', 'facebook').
    """

    # Username on the given service. For example, jane.doe for the user
    # jane.doe on Facebook, and jane.doe@gmail.com for said email address.
    handle = models.CharField(max_length=100,
                              validators=[validate_handle])

    # Name of service where this handle originates.
    #
    # Current valid values are:
    #   * email
    #   * facebook
    service = models.CharField(max_length=20,
                               validators=[validate_service])

    # Face that this agent belongs to.
    owner = models.ForeignKey(Face, default=lambda: Face.objects.create())

    # Options
    class Meta:
        unique_together = (('handle', 'service'))


class PendingClaim(models.Model):
    """
    Pending Claim data model.


    Represents a pending claim to a face by a user.
    """

    # Claimer
    claimer = models.ForeignKey(Profile)

    # Face being claimed
    face = models.ForeignKey(Face)

    def generate_ckey():
        """
        Generates a unique confirmation key.

        The checking here for duplicates is, statistically, pretty unnecessary.
        But this stuff isn't on the critical path, so why not?
        """

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


class ConfidantLink(models.Model):
    """
    Confidant relationship data model.

    Confidants relationships are always bidirectional. Alice cannot receive
    information from Bob unless she's willing to share information with him
    too. However, each person may set the propagation coefficient on
    information flowing from the other. As such, we represent each confidant
    relationship as two separate objects, and maintain the invariant that they
    must exist in pairs.

    TODO: add validation for the above invariant.
    """

    # The source and destination of a confidant link are both Face objects.
    src = models.ForeignKey(Face, related_name='confidant_out_links')
    dst = models.ForeignKey(Face, related_name='confidant_in_links')

    # Propagation coefficient - how much does information through this link
    # propagate?
    prop_coef = models.PositiveSmallIntegerField(validators=[
                                                   validate_prop_coef])


class TagSet(models.Model):
    """Data model for a collection of tags placed on a face."""

    # The tagger and target are both Face objects.
    tagger = models.ForeignKey(Face, related_name='tagsets_by')
    target = models.ForeignKey(Face, related_name='tagsets_for')

    class Meta:
        unique_together = (('tagger', 'target'))


class Tag(models.Model):
    """
    Tag data model.

    A tag is the fundamental unit of information in Rainbeard. It consists of a
    name (whose semantics are left completely to the beholder), an confidence
    value representing the strength of the opinion, a tagger, and a target. The
    tagge and target are coalesced into the TagSet object to economize on
    storage.
    """

    # Name of the tag
    name = models.SlugField(max_length=40)

    # Confidence given to the tag
    confidence = models.PositiveSmallIntegerField(validators=[
                                                    validate_confidence])

    # TagSet this tag corresponds to
    tagset = models.ForeignKey(TagSet)
