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

from ..models import ShippingAddress, ShipperInfo
from backend.views import (
	create_user,
	login_user,
	login_user_web,
)

from ..forms import RegistrationForm

import re


def get_username_from_email(email):
	return re.sub(r"@|\.", r"", email)
	# return email


def register(request):
	"""
	Load the registration page
	"""
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			data_dict = {x: v for x, v in request.POST.items()}
			data_dict["social_auth"] = "none"
			create_user(**data_dict)
			return redirect('friendship:login')
	else:
		form = RegistrationForm()
	return render(request, 'friendship/register.html', {'form': form})


def login_view(request):
	"""
	load login view.
	"""
	if "next" in request.GET:
		request.session["next"] = request.GET["next"]
	return render(request, 'friendship/login.html', {})


def login_process(request):
	"""
	Process login
	"""
	try:
		data_dict = {x: v for x, v in request.POST.items()}
		login_user_web(request, **data_dict)
		if 'next' in request.session:
			return redirect(request.session["next"])
		if request.session["is_shipper"] == True:
			return HttpResponseRedirect(reverse('friendship:sender_landing'))
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

def account(request):
	return render(request, 'friendship/account.html', {
		'data': [request, ],
	})

def become_sender(request):
	return render(request, 'friendship/become_sender.html', {
		'data': [request, ],
	})

