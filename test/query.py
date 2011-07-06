"""Confidant network query unit tests."""

from unittest import TestLoader, TestSuite
from django.test import TestCase

from rainbeard.models import *
from rainbeard import query
import util


class SimpleQueryTestcase(TestCase):
    fixtures = ['identities.json', 'tags.json']

    def setUp(self):

        # Dummy query, for now.
        results = query.do_query(Face.objects.get(label='Andi'),
                                 Face.objects.get(label='Ben'))
        self.assertEqual(results['Nice'], 5)


def suite():
    return TestSuite([TestLoader().loadTestsFromTestCase(SimpleQueryTestcase)])
