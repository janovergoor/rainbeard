from unittest import TestLoader, TestSuite
from django.test import TestCase
from rainbeard.models import *
from rainbeard import query
from . import util


class SimpleQueryTestcase(TestCase):
  fixtures = ['identities.json', 'tags.json']

  def setUp(self):
    
    # import identities fixture
    # import tag fixture
    True

  def test_basic(self):

    # Dummy query, for now.
    results = query.do_query(Face.objects.get(label="Andi"),
                             Face.objects.get(label="Ben"))
    self.assertEqual(results['Nice'], 5)  # Note: confidence field doens't get 0.5, but it does get 5 ??

def suite():
  return TestSuite([TestLoader().loadTestsFromTestCase(SimpleQueryTestcase)])
