""" Data import module tests."""

import os

from unittest import TestLoader, TestSuite
from django.test import TestCase

import importer


class SimpleImporterTestcase(TestCase):
    
    def test_basic(self):
        
        # Create very simple data structures.
        net = {1:2, 2:3}
        importer.SaveConfidantNetwork(net, 'newnetwork')

        # Import the same network.
        net = importer.LoadConfidantNetwork('newnetwork')
        self.assertEqual(type(net), dict)
        self.assertEqual(net[1], 2)
        os.remove('rainbeard/data/newnetwork.p')
        
        # Use default file name.
        importer.SaveConfidantNetwork(net)
        os.remove('rainbeard/data/network.p')

def suite():
    return TestSuite([TestLoader().loadTestsFromTestCase(SimpleImporterTestcase)])
