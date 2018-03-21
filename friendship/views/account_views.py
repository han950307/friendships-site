from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.contrib.auth.models import User
from django.http import (
    HttpResponseRedirect
)
from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)
from django.urls import reverse

from ..models import UserInfo

import re


def register(request):
    """
    Load the registration page
    """
    return render(request, 'friendship/register.html', {})


def register_process(request):
    """
    Process registration and put user data into the database.
    """
    # Trying to get the items.
    try:
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        address = request.POST['address']
        phone = request.POST['phone']
    except KeyError:
        error(request, 'You did not fill out a field.')
        return render(request, 'friendship/register.html', {})
    else:
        # hack for generating a username from email.
        uname = re.sub(r"@|\.", r"", email)

        # Check whether this email exists in the database already.
        obj = User.objects.filter(username=uname)
        if obj:
            error(request, 'The email \'{}\' is already registered.'.format(email))
            return render(request, 'friendship/register.html', {})
        user = User.objects.create_user(
            uname,
            email,
            password
        )
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.is_superuser = False
        user.is_staff = False
        user.is_active = True
        user.save()

        user_id = user.id
        user_info = UserInfo.objects.create(
            shipping_address=address,
            phone=phone,
            is_receiver=True,
            is_shipper=False,
            user=user
        )

        return redirect('friendship:login')


def login_view(request):
    """
    load login view.
    """
    return render(request, 'friendship/login.html', {})


def login_process(request):
    """
    Process login
    """
    try:
        # hack for generating a username from email
        username = re.sub(r"@|\.", r"", request.POST['email'])
        password = request.POST['password']
    except KeyError:
        return render(request, 'friendship/login.html', {
            error(request, 'You didn\'t fill out something')
        })
    else:
        # Use username to authenticate. LOL this is so bad
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            user_info = UserInfo.objects.get(pk=user)
            request.session["is_shipper"] = user_info.is_shipper
            return HttpResponseRedirect(reverse('friendship:index'))
        else:
            error(request, 'Did not find a match.')
            return render(request, 'friendship/login.html', {})


def logout_view(request):
    """
    Logs a user out :P
    """
    logout(request)
    error(request, 'Successfully Logged out.')
    return redirect('friendship:login')