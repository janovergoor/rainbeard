#
# Code relating to account management
#

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import validators
from models import *

# Add a user account
# TODO - Make this a transaction?
def register_user(username, password, email, send_email=True):

  # Create the user account
  user = User.objects.create_user(username, email, password=password)
  user.is_active = False
  user.save()

  # Create the user profile (extra rainbeard-specific user data)
  profile = Profile(user=user)
  profile.save()

  # Create the default identity. This starts active.
  identity = Identity(label='default', profile=profile, is_active=True)
  identity.save()

  # Request a claim on the email address
  request_claim(identity, handle=email, service='email',
                quiet=(not send_email))


# Requests to claim. Returns the claim object if one is created, None otherwise.
#
# The caller should verify that the agent has not already been claimed
def request_claim(identity, handle, service, quiet=False):

  # Make sure the agent is in the database
  agent, created = Agent.objects.get_or_create(handle=handle, service=service)

  # The agent should be unknowned
  if agent.owner != None:
    raise Exception('Trying to claim agent that already has an owner!')

  # If there's already a pending claim for us, don't do anything
  if PendingClaim.objects.filter(owner=identity, handle=handle,
                                 service=service).count() != 0:
    return None

  # Add a pending claim
  claim = PendingClaim(owner=identity, handle=handle, service=service)
  claim.save()

  # We don't handle sending the message yet
  if not quiet:
    raise Exception("We don't handle sending messages yet!")

  # Done
  return claim

#
# Carries out a claim given a confirmation key.
#
# Returns the agent claimed on success, None on failure.
#
def do_claim(ckey):

  # Find the relevant entry
  try:
    claim = PendingClaim.objects.get(ckey=ckey)
  except PendingClaim.DoesNotExist:
    return None

  # Copy the relevant data for convenience
  (handle, service, identity) = (claim.handle, claim.service, claim.owner)

  # There should already be an agent if there are pending claims. Find it
  # and set the owner
  agent = Agent.objects.get(handle=handle, service=service)
  agent.owner = identity
  agent.save()

  # Delete all pending claims to this agent
  PendingClaim.objects.filter(handle=handle, service=service).delete()

  # If this is the email account waiting for user activation, activate
  if service == 'email' and handle == identity.profile.user.email:
    identity.profile.user.is_active = True
    identity.profile.user.save()

  # All done
  return agent

#
# Form definitions
#

class LoginForm(forms.Form):
  username = forms.CharField(max_length=30)
  password = forms.CharField(widget=forms.PasswordInput())
  next = forms.CharField(widget=forms.HiddenInput())

  # Validation
  def clean(self):

    # Store the incoming cleaned data
    data = self.cleaned_data

    # Validate credentials
    if (set(('username', 'password')) <= set(data)):
      user = authenticate(username=data['username'],
                          password=data['password'])
      if user is None:
        raise forms.ValidationError('Invalid login.')
      if not user.is_active:
        raise forms.ValidationError('This account has not yet been activated or has been disabled.')

      # Save the user object so that we don't have to call authenticate() twice
      data['userobj'] = user

    # Make sure to return the new cleaned_data
    return data


class RegForm(forms.Form):
  username = forms.CharField(max_length=30,label='Pick a Username',
                             validators=[validators.validate_new_username])
  email = forms.EmailField(label='Your Email',
                           validators=[validators.validate_new_email])
  password = forms.CharField(widget=forms.PasswordInput(),label='New Password')
  password_confirmation = forms.CharField(widget=forms.PasswordInput(),
                                          label='Confirm Password')

  # Validation
  def clean(self):

    # Store the incoming cleaned data
    data = self.cleaned_data

    # Check that the passwords match
    if set(('password', 'password_confirmation')) <= set(data):
      if data['password'] != data['password_confirmation']:
        raise forms.ValidationError('Passwords do not match.')

    # Return the cleaned data
    return data
