from django import forms
from django.core.validators import *
from django.contrib.auth.models import User
import common

#
# Validators for various bits of user input
#

# Agent handles
validate_handle = RegexValidator('[a-zA-z0-9_&\.\+=]+')

# Agent service
def validate_service(service):
  if service not in set(common.services):
    raise ValidationError('Invalid Service')

# Confidence values
def validate_confidence(confidence):
  if confidence % 2 == 0 or confidence < 1 or confidence > 9:
    raise ValidationError('Invalid confidence value')


# Propagation coefficients (as fractions of 4)
# 0 <-> 0
# 1 <-> 1/4
# 2 <-> 2/4
# 3 <-> 3/4
# 4 <-> 1
def validate_prop_coef(coef):
  if coef < 0 or coef > 4:
    raise ValidationError('Invalid Propagation Coefficient')


# Validate an ajax request post
#
# Throws an error if it doesn't recognize one of the parameters
def validate_ajax_params(params):
  for key,value in params.items():
    if key == 'handle':
      validate_handle(value)
    elif key == 'service':
      validate_service(value)
    else:
      raise ValidationError('Unknown POST parameter')


# Validate a new username to make sure it doesn't exist.
#
# NB: The astute coder will notice the potential for a TOCTOU race condition
# in which another account for this username is created in the window between
# the validation here and the actual creation. However, the username field in
# the User model is set to unique=True, meaning that the db layer will raise
# an IntegrityError upon final creation. This is nasty for the UX in that
# case (the user will get a 500 error when trying to create an account), but
# data integrity will be preserved.
def validate_new_username(username):
  if User.objects.filter(username=username).count() != 0:
    raise forms.ValidationError('Username already exists in the system.')

# Check if the given email already belongs to an active user.
#
# Unlike above, the email field in the User table does not have unique=True.
# Luckily, having multiple users with the same email address in the Users
# database is pretty benign. In fact, it could happen: mallory tries to
# register an account with bob's email address, and her account remains in
# perpetual limbo because she's unable to confirm her email address. Later
# on, Bob comes and claims his account.
#
# So we can have multiple User objects with the same email address. What we
# don't want is to have multiple _active_ users with the same email address.
# To prevent this, we rely on the unique_together enforcement that happens
# when we add a new agent. When we confirm a user's email address, we add
# and Agent _before_ setting the user to active. So any duplication is
# detected in the Agent-creation phase and we can never activate a user with
# a duplicate email address.
#
# All of the above is really just for robustness/security though. We'd still
# like to handle the common case with a nice warning rather than an exception.
# So do that.
def validate_new_email(email):
  if User.objects.filter(email=email,is_active=True).count() != 0:
    raise forms.ValidationError('The email address provided already ' +
                                'exists in the system.')
