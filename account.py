"""Account management module."""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import validators
import identity
from models import *


# TODO - Should this be a transaction?
def register_user(username, password, email, send_email=True):
    """
    Adds a user account.

    Returns a Django model object corresponding to the created user.
    """

    # Doean Agent/Identity exist for this email address? If not, make them.
    # While we're at it, make sure that the email address is unclaimed.
    emailface = identity.get_face(email, 'email', create=True)
    if emailface.owner is not None:
        raise Exception('Trying to register user, but email address ' + email +
                        ' already claimed.')

    # Create the user account.
    user = User.objects.create_user(username, email, password=password)
    user.is_active = False
    user.save()

    # Create the user profile (extra rainbeard-specific user data).
    profile = Profile(user=user)
    profile.save()

    # Request a claim on the email address.
    request_claim(profile, emailface, quiet=(not send_email))

    return user


def request_claim(claimer, face, quiet=False):
    """
    Requests to claim a face on behalf of a user.

    A claim represents an attempt by a user to associate an unbound Agent (via
    its associated unbound Face) with his/her account. The ensure that this
    claim is legitimate, we generate a secret confirmation key, store it in the
    database, and send the key to the account being claimed (via email,
    facebook message, etc).

    Claiming is thus a two-step process. There must be a corresponding call to
    do_claim() in order for the association to be finalized.

    Arguments:
    claimer - The user doing the claim, represented by a Profile model.
    face - The Face object being claimed.
    quiet - Whether the claim message should be sent. Passing False here is
            useful for unit testing.

    If the face already has an owner, an exception will be raised.
    """

    # The face should be unbound.
    if face.owner != None:
        raise Exception('Trying to claim a face that already has an owner!')

    # If there's already a pending claim for us, don't do anything.
    if PendingClaim.objects.filter(claimer=claimer, face=face).count() != 0:
        return None

    # Add a pending claim.
    claim = PendingClaim(claimer=claimer, face=face)
    claim.save()

    # We don't handle sending the message yet.
    if not quiet:
        raise Exception("We don't handle sending messages yet!")

    # All done!
    return claim


def do_claim(ckey):
    """
    Carries out a claim given a confirmation key.

    This is the second part of the claim process begun in request_claim().

    Returns the claimed face if the claim is successful, None otherwise.
    """

    # Find the relevant entry.
    try:
        claim = PendingClaim.objects.get(ckey=ckey)
    except PendingClaim.DoesNotExist:
        return None

    # Keep direct references here for convenience.
    claimer = claim.claimer
    face = claim.face

    # Do the claim.
    face.owner = claimer
    face.save()

    # Delete all other pending claims to this agent.
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

    # All done!
    return face


class LoginForm(forms.Form):
    """Django form for user login."""

    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())
    next = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        """Django form validation method. Called automatically."""

        # Store the incoming cleaned data.
        data = self.cleaned_data

        # Validate the credentials.
        if (set(('username', 'password')) <= set(data)):
            user = authenticate(username=data['username'],
                                password=data['password'])
            if user is None:
                raise forms.ValidationError('Invalid login.')
            if not user.is_active:
                raise forms.ValidationError('This account has not yet been ' +
                                            'activated or has been disabled.')

            # Save the user object so that we don't have to call authenticate()
            # twice.
            data['userobj'] = user

        # Make sure to return the new cleaned_data.
        return data


class RegForm(forms.Form):
    """Django form for user registration."""

    username = forms.CharField(max_length=30,label='Pick a Username',
                               validators=[validators.validate_new_username])
    email = forms.EmailField(label='Your Email',
                             validators=[validators.validate_new_email])
    password = forms.CharField(widget=forms.PasswordInput(),
                               label='New Password')
    password_confirmation = forms.CharField(widget=forms.PasswordInput(),
                                            label='Confirm Password')

    def clean(self):
        """Django form validation method. Called automatically."""

        # Store the incoming cleaned data.
        data = self.cleaned_data

        # Check that the passwords match.
        if set(('password', 'password_confirmation')) <= set(data):
            if data['password'] != data['password_confirmation']:
                raise forms.ValidationError('Passwords do not match.')

        # Return the cleaned data.
        return data
