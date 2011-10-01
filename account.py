"""Account management module."""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import validators, identity
from models import *

# Add a user account. Returns the created user object.
# TODO - Make this a transaction?
def register_user(username, password, email, send_email=True):

  # Doean Agent/Identity exist for this email address? If not, make them.
  # While we're at it, make sure that the email address is unclaimed.
  emailface = identity.get_face(email, 'email', create=True)
  if emailface.owner is not None:
    raise Exception('Trying to register user, but email address ' + email + ' already claimed.')

  # Create the user account
  user = User.objects.create_user(username, email, password=password)
  user.is_active = False
  user.save()

  # Create the user profile (extra rainbeard-specific user data)
  profile = Profile(user=user)
  profile.save()

  # Request a claim on the email address
  request_claim(profile, emailface, quiet=(not send_email))

  return user


# Requests to claim a face. Returns the claimed face if one is created, None
# otherwise.
#
# The caller should verify that the face has not already been claimed
def request_claim(claimer, face, quiet=False):

  # The face should be unbound
  if face.owner != None:
    raise Exception('Trying to claim a face that already has an owner!')

  # If there's already a pending claim for us, don't do anything
  if PendingClaim.objects.filter(claimer=claimer, face=face).count() != 0:
    return None

  # Add a pending claim
  claim = PendingClaim(claimer=claimer, face=face)
  claim.save()

  # We don't handle sending the message yet
  if not quiet:
    raise Exception("We don't handle sending messages yet!")

  # Done
  return claim

#
# Carries out a claim given a confirmation key.
#
# Returns the face claimed on success, None on failure.
#
def do_claim(ckey):

  # Find the relevant entry
  try:
    claim = PendingClaim.objects.get(ckey=ckey)
  except PendingClaim.DoesNotExist:
    return None

  # Save for convenience
  claimer = claim.claimer
  face = claim.face

  # Do the claim
  face.owner = claimer
  face.save()

  # Delete all other pending claims to this agent
  PendingClaim.objects.filter(face=face).delete()

  # It's possible that this corresponds to a new user carrying out email
  # activation. If so, handle that here.
  if not claimer.active_face():
    assert not claimer.user.is_active
    face.is_active = True
    face.label = 'default'
    face.save()
    claimer.user.is_active = True
    claimer.user.save()

  # All done
  return face

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
