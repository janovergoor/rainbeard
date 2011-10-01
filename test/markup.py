"""
Markup validation unit test shim.

This module hooks a markup validator into our unit test framework, allowing us
to automatically validate the markup we generate.
"""

from unittest import TestLoader, TestSuite

from django.test import TestCase
from django.test.client import Client
from tidylib import tidy_document

import util

class MarkupValidatorTestcase(TestCase):

  def setUp(self):

    # Give us a logged in client
    user = util.make_user('bob')
    self.c = Client()
    self.c.login(username='bob', password='bobpass')

  def validate_content(self, content):
    doc, err = tidy_document(content)
    self.assertEqual(err, '')

  def test_login_page(self):
    response = Client().get('/login')
    self.validate_content(response.content)

  def test_reg_page(self):
    response = Client().get('/register')
    self.validate_content(response.content)

  def test_main_page(self):
    response = self.c.get('/')
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/main.html')
    self.validate_content(response.content)

  def test_query_page(self):
    util.make_user('charlie')
    response = self.c.get('/query?handle=charlie@example.com&service=email')
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/query.html')
    self.validate_content(response.content)

def suite():
  return TestLoader().loadTestsFromTestCase(MarkupValidatorTestcase)
