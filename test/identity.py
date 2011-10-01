"""Identity management unit tests."""

from unittest import TestLoader, TestSuite

from django.test import TestCase
from django.contrib.auth.models import User

from rainbeard import account
from rainbeard import identity
from rainbeard.models import *

class SimpleIdentityTestcase(TestCase):

    def setUp(self):

        # Make some accounts
        account.register_user('alice', 'alicepass', 'alice@example.com', False)
        account.register_user('bob', 'bobpass', 'bob@example.com', False)
        account.register_user('charlie', 'charliepass', 'charlie@example.com', False)

    def test_basic(self):

        # Get a face that exists
        self.assertNotEqual(identity.get_face('alice@example.com', 'email', create=False), None)

        # Make 2 face/agent pairs
        foo_face = identity.get_face('foo', 'facebook', create=True)
        bar_agent = identity.get_agent('bar', 'facebook', create=True)

        # Look one up using the opposite function
        self.assertEqual(foo_face, identity.get_agent('foo', 'facebook').owner)

        # Trigger some exceptions
        try:
            identity.get_face('dne', 'facebook', create=False)
        except Face.DoesNotExist:
            caught_dne_face = True
        try:
            identity.get_agent('dne', 'facebook', create=False)
        except Agent.DoesNotExist:
            caught_dne_agent = True

        # Verify
        self.assertTrue(caught_dne_face)
        self.assertTrue(caught_dne_agent)

def suite():
    return TestSuite([TestLoader().loadTestsFromTestCase(SimpleIdentityTestcase)])
