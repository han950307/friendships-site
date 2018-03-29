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

from ..models import ShippingAddress, ShipperList

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

        shipping_address = ShippingAddress.objects.create(
            user=user,
            address=address,
            phone=phone,
            address_type=ShippingAddress.AddressType.RECEIVER_ADDRESS,
            primary=True,
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

            # check if the user is a shipper.
            user = ShipperList.objects.filter(pk=user)
            if user:
                request.session["is_shipper"] = True
                return HttpResponseRedirect(reverse('friendship:index'))
            else:
                request.session["is_shipper"] = False
                return HttpResponseRedirect(reverse('friendship:receiver_landing'))

        else:
            error(request, 'Did not find a match.')
            return render(request, 'friendship/login.html', {})

def logout_view(request):
    """
    Logs a user out :P
    """
    logout(request)
    return redirect('friendship:login')