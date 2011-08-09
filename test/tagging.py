from unittest import TestLoader, TestSuite
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.utils import simplejson as json
from rainbeard import account, tagging
from rainbeard.models import *
from . import util


class SimpleTaggingTestcase(TestCase):

  def setUp(self):

    # Make some accounts
    aliceuser = util.make_user('alice', 'alicepass', 'alice@example.com')
    bobuser = util.make_user('bob', 'bobpass', 'bob@example.org')
    charlieuser = util.make_user('charlie', 'charliepass', 'charlie@example.com')

    # Cache their identities
    self.face_alice = aliceuser.get_profile().active_face()
    self.face_bob = bobuser.get_profile().active_face()
    self.face_charlie = charlieuser.get_profile().active_face()

    # Set some tags
    self.tags_alicetobob = {'trustworthy': 7, 'funny': 3, 'reliable': 5}
    tagging.set_tagset(self.face_alice, self.face_bob, self.tags_alicetobob)


  def test_basic(self):

    # Read the tags back and verify
    self.assertEqual(tagging.get_tagset(self.face_alice, self.face_bob),
                     self.tags_alicetobob)


  def test_empty(self):

    # Set an empty tagset on alice, and don't even set one on bob
    tagging.set_tagset(self.face_charlie, self.face_alice, {})

    # Verify
    self.assertEqual(tagging.get_tagset(self.face_charlie, self.face_alice), {})
    self.assertEqual(tagging.get_tagset(self.face_charlie, self.face_bob), {})


  def test_bidirectional(self):

    # Set some other tags from bob to alice
    tags_bobtoalice = {'bizarre': 9, 'funny': 9, 'trustworthy': 7}
    tagging.set_tagset(self.face_bob, self.face_alice, tags_bobtoalice)

    # Read the tags back and verify
    self.assertEqual(tagging.get_tagset(self.face_alice, self.face_bob),
                     self.tags_alicetobob)
    self.assertEqual(tagging.get_tagset(self.face_bob, self.face_alice),
                     tags_bobtoalice)


  def test_add(self):

    # Add some tags
    self.tags_alicetobob['skinny'] = 3
    self.tags_alicetobob['fat'] = 9

    # Write
    tagging.set_tagset(self.face_alice, self.face_bob, self.tags_alicetobob)

    # Verify
    self.assertEqual(tagging.get_tagset(self.face_alice, self.face_bob),
                     self.tags_alicetobob)

  def test_remove(self):

    # Remove a tag
    del self.tags_alicetobob['trustworthy']

    # Write
    tagging.set_tagset(self.face_alice, self.face_bob, self.tags_alicetobob)

    # Verify
    self.assertEqual(tagging.get_tagset(self.face_alice, self.face_bob),
                     self.tags_alicetobob)

  def test_modify(self):

    # Modify a tag
    self.tags_alicetobob['reliable'] = 1

    # Write
    tagging.set_tagset(self.face_alice, self.face_bob, self.tags_alicetobob)

    # Verify
    self.assertEqual(tagging.get_tagset(self.face_alice, self.face_bob),
                     self.tags_alicetobob)

  def test_addremovemodify(self):

    # Do all 3
    self.tags_alicetobob['skinny'] = 3
    del self.tags_alicetobob['trustworthy']
    self.tags_alicetobob['reliable'] = 1

    # Write
    tagging.set_tagset(self.face_alice, self.face_bob, self.tags_alicetobob)

    # Verify
    self.assertEqual(tagging.get_tagset(self.face_alice, self.face_bob),
                     self.tags_alicetobob)


# Do tag manipulation over the ajax interface
class AjaxTaggingTestcase(TestCase):

  def setUp(self):

    # Make some accounts
    aliceuser = util.make_user('alice', password='alicepass')
    bobuser = util.make_user('bob', email='bob@example.org')

    # Set some tags
    self.tags_alicetobob = {'trustworthy': 7, 'funny': 3, 'reliable': 5}
    tagging.set_tagset(aliceuser.get_profile().active_face(),
                       bobuser.get_profile().active_face(), self.tags_alicetobob)


  def test_basic(self):

    # Log in
    client = Client()
    client.login(username='alice', password='alicepass')

    # Make the ajax request
    response = client.post('/ajax/givens/get', {'handle': 'bob@example.org',
                                                'service': 'email'})

    # Parse
    tags = json.loads(response.content)['tags']

    # Verify
    self.assertEqual(tags, self.tags_alicetobob)

def suite():
  return TestSuite([TestLoader().loadTestsFromTestCase(SimpleTaggingTestcase),
                    TestLoader().loadTestsFromTestCase(AjaxTaggingTestcase)])

