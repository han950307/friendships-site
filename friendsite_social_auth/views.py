from django.shortcuts import (
    render,
    redirect,
)

from friendsite.settings import (
	FACEBOOK_CLIENT_ID,
	FACEBOOK_CLIENT_SECRET,
	FACEBOOK_REDIRECT_URI,
	DEBUG,
)

from backend.views import (
	facebook_auth_token_is_valid,
	login_user,
)

import json
import requests


# Create your views here.
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

	try:
		user_token = response_dict["access_token"]
		data_dict = {
			"social_auth": "facebook",
			"user_token": user_token
		}
	except:
		error(request, "Failed logging into facebook.")
		redirect("friendship:index")

	valid, response_dict = facebook_auth_token_is_valid(**data_dict)

	if valid:
		response = requests.get("https://graph.facebook.com/v2.12me?access_token="
					.format(user_token))

	content = response.content
	print(content)
	return render(request, 'friendship/testing.html', {'data': content})
