from unittest import TestLoader, TestSuite
from django.test import TestCase
from rainbeard import importer
import os

class SimpleImporterTestcase(TestCase):
    
  def test_basic(self):
        
    # Create very simple datastructures
    net  = {1:2, 2:3}
    importer.SaveConfidantNetwork(net,"newnetwork")

    # import the same network
    net = importer.LoadConfidantNetwork("newnetwork")
    self.assertEqual(type(net), dict)
    self.assertEqual(net[1], 2)
    os.remove("rainbeard/data/newnetwork.p")
    
    # use default file name
    importer.SaveConfidantNetwork(net)
    os.remove("rainbeard/data/network.p")


def suite():
  return TestSuite([TestLoader().loadTestsFromTestCase(SimpleImporterTestcase)])
