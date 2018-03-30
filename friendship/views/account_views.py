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
from backend.views import (
	create_user,
	login_user,
)

import re


def get_username_from_email(email):
	# return re.sub(r"@|\.", r"", email)
	return email


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
		create_user(**request.POST)
	except (KeyError, ValueError):
		return render(request, 'friendship/register.html', {})
	
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
		login_user(request, **request.POST)
	    if request.session["is_shipper"] == True
	        return HttpResponseRedirect(reverse('friendship:index'))
	    else:
	        return HttpResponseRedirect(reverse('friendship:receiver_landing'))
	except (KeyError, ValueError) as e:
		return render(request, 'friendship/login.html', {"error": str(e)})
	else:
		return HttpResponseRedirect(reverse('friendship:index'))


def logout_view(request):
    """
    Logs a user out :P
    """
    logout(request)
    return redirect('friendship:login')
