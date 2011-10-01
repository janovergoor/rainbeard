"""Account management unit tests."""

from unittest import TestLoader, TestSuite

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from rainbeard import account
from rainbeard.models import *
import util

class SimpleAccountTestcase(TestCase):

  def setUp(self):

    # Make some accounts
    account.register_user('alice', 'alicepass', 'alice@example.com', False)
    account.register_user('bob', 'bobpass', 'bob@example.com', False)
    account.register_user('charlie', 'charliepass', 'charlie@example.com', False)

  def test_basic(self):

    # Accounts should start inactive
    user = User.objects.get(username='alice')
    self.assertFalse(user.is_active)

    # There should be a corresponding profile
    profile = user.get_profile()
    self.assertNotEqual(profile, None)

  # Claim the email used in registration
  def test_good_email_claim(self):
    bobuser = User.objects.get(username='bob')
    self.assertFalse(bobuser.is_active)
    face = account.do_claim(PendingClaim.objects.get(claimer=bobuser.get_profile()).ckey)
    self.assertEqual(face.owner.user, bobuser)
    self.assertTrue(User.objects.get(username='bob').is_active)

  # Claim with a nonexistant key
  def test_bad_claim(self):
    agent = account.do_claim(''.join('f' for x in range(common.ckey_length)))
    self.assertEqual(agent, None)

# Create accounts and log in through the web interface
class UIAccountTestcase(TestCase):

  # Create some accounts
  def setUp(self):
    account.register_user('alice', 'alicepass', 'alice@example.com', False)
    util.make_user('bob') # make_user activates the user too

  #
  # Test a good registration
  #
  def test_good_registration(self):
    self.assertEqual(User.objects.filter(username='charlie').count(), 0)
    response = Client().post('/register', {'username': 'charlie',
                                           'email': 'charlie@example.com',
                                           'password': 'pass',
                                           'password_confirmation': 'pass'})
    self.assertEqual(User.objects.filter(username='charlie').count(), 1)


  #
  # Test all the ways in which we can make faulty accounts
  #

  def test_preexisting_username(self):
    response = Client().post('/register', {'username': 'alice',
                                           'email': 'alice@example.com',
                                           'password': 'pass',
                                           'password_confirmation': 'pass'})
    errors = response.context['form'].errors
    self.assertTrue('username' in response.context['form'].errors)
    self.assertTrue('email' not in response.context['form'].errors)
    self.assertEqual(len(response.context['form'].non_field_errors()), 0)

  def test_claimed_email(self):
    response = Client().post('/register', {'username': 'bobster',
                                           'email': 'bob@example.com',
                                           'password': 'pass',
                                           'password_confirmation': 'pass'})
    errors = response.context['form'].errors
    self.assertTrue('username' not in response.context['form'].errors)
    self.assertTrue('email' in response.context['form'].errors)
    self.assertEqual(len(response.context['form'].non_field_errors()), 0)

  def test_password_mismatch(self):
    response = Client().post('/register', {'username': 'bobster',
                                           'email': 'bobster@example.com',
                                           'password': 'pass',
                                           'password_confirmation': 'paste'})
    errors = response.context['form'].errors
    self.assertTrue('username' not in response.context['form'].errors)
    self.assertTrue('email' not in response.context['form'].errors)
    self.assertEqual(len(response.context['form'].non_field_errors()), 1)


  # Test 'next' url tracking
  def test_next_url(self):
    client = Client()
    response = client.get('/query', follow=True)
    self.assertEqual(response.context['form'].initial['next'], '/query')


  # Test a good login
  def test_good_login(self):

    # Log in
    response = Client().get('/', follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/login.html')
    response = response.client.post('/login', {'username': 'bob',
                                               'password': 'bobpass',
                                               'next': '/'}, 
                                    follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/main.html')

    # Make sure we can't get back to the login page
    response = response.client.get('/login', follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/main.html')

    # Make sure we can't get to the registration page
    response = response.client.get('/register', follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/main.html')

    # Log out
    response = response.client.get('/logout')
    response = Client().get('/', follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/login.html')


  # Test an incorrect password
  def test_bad_password_login(self):
    response = Client().get('/', follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/login.html')
    response = response.client.post('/login', {'username': 'bob',
                                               'password': 'badpass',
                                               'next': '/'}, 
                                    follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/login.html')

  # Test an inactive login
  def test_inactive_login(self):
    response = Client().get('/', follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/login.html')
    response = response.client.post('/login', {'username': 'alice',
                                               'password': 'alicepass',
                                               'next': '/'}, 
                                    follow=True)
    self.assertEqual(response.templates[0].name, 'rainbeard/templates/login.html')
    self.assertEqual(len(response.context['form'].non_field_errors()), 1)

def suite():
  return TestSuite([TestLoader().loadTestsFromTestCase(SimpleAccountTestcase),
                    TestLoader().loadTestsFromTestCase(UIAccountTestcase)])
