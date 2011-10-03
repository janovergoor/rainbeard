"""
View module.

When Django receives a request, it examines the URL to determine how it should
proceed. The URL module maps URL patterns to view functions, which are defined
here.

View functions should do the minimum possible to service the request. Any heavy
lifting should occur in other modules.
"""
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import account


def register_view(request):

    # If we're authenticated, don't let us log in again.
    if request.user.is_authenticated():
        return redirect('/')

    # Try processing the form if we have it.
    if request.method == 'POST':

        # Create a form from the POST data.
        form = account.RegForm(request.POST)

        # If it appears to be valid, create the user.
        if form.is_valid():
            data = form.cleaned_data

            # TODO - send_email=True
            account.register_user(data['username'], data['password'],
                                  data['email'], send_email=False)
            return HttpResponse('An account for the user %s has been ' \
                                'created. A confirmation link as been sent ' \
                                'to %s. You must click the link to activate ' \
                                'your account.' %
                                (data['username'], data['email']))

    # Make a blank form if we don't have it.
    else:
        form = account.RegForm()

    # Display the form.
    return render_to_response('rainbeard/templates/register.html',
                              {'form': form})


def login_view(request, ignored):

    # If we're authenticated, don't let us log in again.
    if request.user.is_authenticated():
        return redirect('/')

    # Try processing the form if we have it.
    if request.method == 'POST':

        # Create a form from the POST data.
        form = account.LoginForm(request.POST)

        # If it's a valid user, log us in and redirect.
        if form.is_valid():
            login(request, form.cleaned_data['userobj'])
            return redirect(form.cleaned_data['next'])

    # Make a blank one if we don't.
    else:
        next = '/'
        if 'next' in request.GET:
            next = request.GET['next']
        form = account.LoginForm(initial={'next': next})

    # Display the form.
    return render_to_response('rainbeard/templates/login.html',
                              {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def main_view(request):

    return render_to_response('rainbeard/templates/main.html',
                              {'username': request.user.username})


@login_required
def query_view(request):

    service = request.GET['service']
    handle = request.GET['handle']

    # Figure out the source for the profile image.
    picsrc = '%sblankprofile.jpg' % settings.STATIC_URL
    if service == "facebook":
        picsrc = 'https://graph.facebook.com/%s/picture?type=large' % handle

    context = {'service': service,
               'handle': handle,
               'picsrc': picsrc}
    return render_to_response('rainbeard/templates/query.html', context)
