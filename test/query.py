from unittest import TestLoader, TestSuite
from django.test import TestCase
from rainbeard.models import *
from rainbeard import query
from . import util


class SimpleQueryTestcase(TestCase):

  def setUp(self):

    # Create two basic user accounts with email addresses
    self.alice = util.make_user('alice')
    self.bob = util.make_user('bob')

  def test_basic(self):

    # Dummy query, for now.
    results = query.do_query(self.alice.get_profile().active_identity(),
                             self.bob.get_profile().active_identity())
    self.assertEqual(results['reliable'], 0.5)

def suite():
  return TestSuite([TestLoader().loadTestsFromTestCase(SimpleQueryTestcase)])
