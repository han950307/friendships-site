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
				  "&client_secret={app_secret}" + \
				  "&code={code_parameter}"

	url = request_url.format(
		client_id=FACEBOOK_CLIENT_ID,
		redirect_uri=FACEBOOK_REDIRECT_URI,
		client_secret=FACEBOOK_CLIENT_SECRET,
		code=code
	)
	
	response = request.get(url)

	content = response.content
	print(content)
