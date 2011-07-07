from unittest import TestLoader, TestSuite
from django.test import TestCase
from rainbeard.models import *
from rainbeard import query
from . import util


class SimpleQueryTestcase(TestCase):

  # Generate the test data
  # NB: this might need to happen somewhere else
  def setUp(self):

    # Create basic user accounts with email addresses
    self.andi = util.make_user('andi')
    self.ben = util.make_user('ben')
    self.chris = util.make_user('chris')
    self.dan = util.make_user('dan')
    self.ellery = util.make_user('ellery')
    
    # add tag relation : Dan tagged Ellery as 'nice' with strength 1
    util.apply_tag(self.dan.get_profile().active_face(), 
                   self.ellery.get_profile().active_face(), 
                   "nice", 1.0)
    
    # test ConfidantNetwork class
    self.net = ConfidantNetwork()
    self.net.add_link(1, 2, 0.9)
    self.net.add_link(1, 3, 0.7)
    self.net.add_link(2, 1, 0.7)
    self.net.add_link(2, 4, 0.4)
    self.net.add_link(2, 5, 0.6)
    self.net.add_link(3, 1, 0.6)
    self.net.add_link(3, 4, 0.8)
    self.net.add_link(4, 2, 0.3)
    self.net.add_link(4, 3, 0.7)
    self.net.add_link(5, 3, 0.8)
    self.assertEqual(self.net.get_link(1, 2), 0.9)
    self.assertEqual(self.net.get_link(2, 5), 0.6)
    #self.net.print_out()

  def test_basic(self):

    # Andi wants to know about Ellery
    results = query.do_query(self.net,
                             self.andi.get_profile().active_face(),
                             self.ellery.get_profile().active_face())
    self.assertEqual(round(results['nice'],2), 0.56)

def suite():
  return TestSuite([TestLoader().loadTestsFromTestCase(SimpleQueryTestcase)])
