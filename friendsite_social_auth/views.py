from django.shortcuts import (
	render,
	redirect,
)
from django.contrib.messages import error
from django.contrib.auth.models import User
from friendsite.settings import (
	FACEBOOK_CLIENT_ID,
	FACEBOOK_CLIENT_SECRET,
	FACEBOOK_REDIRECT_URI,
	DEBUG,
)

from backend.views import (
	facebook_auth_token_is_valid,
	login_user,
	get_user_auth_token,
	create_user,
)

import json
import requests
import hashlib
import hmac


# Create your views here.
def genAppSecretProof(app_secret, access_token):
	h = hmac.new (
		app_secret.encode('utf-8'),
		msg=access_token.encode('utf-8'),
		digestmod=hashlib.sha256
	)
	return h.hexdigest()


def facebook_login(request):
	"""
	Log in using facebook
	"""
	redirect_url = "https://www.facebook.com/v2.12/dialog/oauth?" + \
				   "client_id={client_id}" + \
				   "&redirect_uri={redirect_uri}" + \
				   "&state={state}"

	url = redirect_url.format(
		client_id=FACEBOOK_CLIENT_ID,
		redirect_uri=FACEBOOK_REDIRECT_URI,
		state="yayimalive"
	)

	return redirect(url)


def facebook_callback(request):
	code = request.GET["code"]

	request_url = "https://graph.facebook.com/v2.12/oauth/access_token?" + \
				  "client_id={client_id}" + \
				  "&redirect_uri={redirect_uri}" + \
				  "&client_secret={client_secret}" + \
				  "&code={code}"

	url = request_url.format(
		client_id=FACEBOOK_CLIENT_ID,
		redirect_uri=FACEBOOK_REDIRECT_URI,
		client_secret=FACEBOOK_CLIENT_SECRET,
		code=code
	)
	
	response = requests.get(url)
	response_dict = json.loads(response.content)

	# Try to see if user token is valid.
	try:
		user_token = response_dict["access_token"]
		data_dict = {
			"social_auth": "facebook",
			"user_token": user_token
		}
		content = response.content
	except:
		print(response_dict)
		error(request, "Failed logging into facebook." + str(response_dict))
		return redirect("friendship:index")

	valid, response_dict = facebook_auth_token_is_valid(**data_dict)

	# If the token is valid, then get user info from facebook.
	if valid:
		user_id = response_dict["data"]["user_id"]
		request_url = "https://graph.facebook.com/v2.12/{user_id}?" + \
					  "fields=id,first_name,last_name,email" + \
					  "&access_token={access_token}" + \
					  "&appsecret_proof={appsecret_proof}"

		url = request_url.format(
			user_id=user_id,
			access_token=user_token,
			appsecret_proof=genAppSecretProof(FACEBOOK_CLIENT_SECRET, user_token)
		)

		response = requests.get(url)
		response_dict = json.loads(response.content)

		# Login user if already exists. else, create user then login.
		data_dict = {x: v for x, v in response_dict.items()}
		data_dict['social_auth'] = 'facebook'
		data_dict['user_token'] = user_token

		try:
			serialized = get_user_auth_token(**data_dict)
		except ValueError:
			user = create_user(**data_dict)
			serialized = get_user_auth_token(**data_dict)

		user = User.objects.get(pk=int(serialized.data["user_id"]))
		login_user(request, user)
	else:
		error(request, "Failed logging into facebook. Please try again.")
		return redirect("friendship:index")

	return render(request, 'friendship/testing.html', {'data': content})
