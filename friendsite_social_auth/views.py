from django.shortcuts import (
    render,
    redirect,
)
from django.views import View
from django.contrib.messages import error
from django.contrib.auth.models import User
from friendsite import settings

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

from urllib.parse import quote


class SocialLoginView(View):
    base_url = None
    client_id = None
    redirect_uri = None
    response_type = "code"
    state = "yayimalive"

    def oauth_request_auth_code(self):
        url = self.base_url + "?" + \
               "client_id=" + quote(self.client_id) + \
               "&response_type=" + quote(self.response_type) + \
               "&redirect_uri=" + quote(self.redirect_uri) + \
               "&state=" + quote(self.state)

        return redirect(url)

    def get(self, request):
        return self.oauth_request_auth_code()


class FacebookSocialLoginView(SocialLoginView):
    base_url = "https://www." + settings.FACEBOOK_API_URL + "/dialog/oauth"
    client_id = settings.FACEBOOK_CLIENT_ID
    redirect_uri = settings.FACEBOOK_REDIRECT_URI

    def get(self, request):
        return super().get(request)


class LineSocialLoginView(SocialLoginView):
    base_url = settings.LINE_AUTH_URL + "weblogin"
    client_id = settings.LINE_CLIENT_ID
    redirect_uri = settings.LINE_REDIRECT_URI

    def get(self, request):
        return super().get(request)


# Create your views here.
def genAppSecretProof(app_secret, access_token):
    h = hmac.new (
        app_secret.encode('utf-8'),
        msg=access_token.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return h.hexdigest()


def facebook_callback(request):
    try:
        code = request.GET["code"]
    except KeyError:
        error(request, "You must grant facebook permission." + str(response_dict))
        return redirect("friendship:index")


    request_url = "https://graph.{fb_api_url}/oauth/access_token?" + \
                  "client_id={client_id}" + \
                  "&redirect_uri={redirect_uri}" + \
                  "&client_secret={client_secret}" + \
                  "&code={code}"

    url = request_url.format(
        client_id=settings.FACEBOOK_CLIENT_ID,
        redirect_uri=settings.FACEBOOK_REDIRECT_URI,
        client_secret=settings.FACEBOOK_CLIENT_SECRET,
        fb_api_url=settings.FACEBOOK_API_URL,
        code=code,
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
        error(request, "Failed logging into facebook." + str(response_dict))
        return redirect("friendship:index")

    valid, response_dict = facebook_auth_token_is_valid(**data_dict)

    # If the token is valid, then get user info from facebook.
    if valid:
        user_id = response_dict["data"]["user_id"]
        request_url = "https://graph.{fb_api_url}/{user_id}?" + \
                      "fields=id,first_name,last_name,email" + \
                      "&access_token={access_token}" + \
                      "&appsecret_proof={appsecret_proof}"

        url = request_url.format(
            user_id=user_id,
            access_token=user_token,
            fb_api_url=settings.FACEBOOK_API_URL,
            appsecret_proof=genAppSecretProof(settings.FACEBOOK_CLIENT_SECRET, user_token),
        )

        response = requests.get(url)
        response_dict = json.loads(response.content)

        # Login user if already exists. else, create user then login.
        data_dict = {x: v for x, v in response_dict.items()}
        data_dict['social_auth'] = 'facebook'
        data_dict['user_token'] = user_token

        # if user token exists, that means they authorized with them.
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

    return redirect("friendship:receiver_landing")


def line_callback(request):
    try:
        code = request.GET["code"]
    except KeyError:
        error(request, "You must grant Line permission to access your account." + str(response_dict))
        return redirect("friendship:index")

    request_url = "https://api.line.me/v2/oauth/accessToken"
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.LINE_CLIENT_ID,
        'client_secret': settings.LINE_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.LINE_REDIRECT_URI,
    }

    response = requests.post(request_url, data)
    response_dict = json.loads(response.content)

    try:
        access_token = response_dict['access_token']
    except KeyError:
        error(request, "Line login failed" + str(response_dict))
        return redirect("friendship:index")

    ## NOW GET USER ID!
    header_dict = {
        'Authorization': 'Bearer {}'.foramt(accessToken)
    }

    request_url = "https://api.line.me/v2/profile"
    response = requests.get(request_url, headers=header_dict)
    response_dict = json.loads(response.content)
    try:
        user_id = response['user_id']
    except KeyError:
        error(request, "Line login failed" + str(response_dict))
        return redirect("friendship:index")

    # Login user if already exists. else, create user then login.
    data_dict = {x: v for x, v in response_dict.items()}
    data_dict['social_auth'] = 'line'
    data_dict['user_token'] = access_token
    data_dict['line_user_id'] = user_id

    # if user token exists, that means they authorized with them.
    try:
        serialized = get_user_auth_token(**data_dict)
    except ValueError:
        user = create_user(**data_dict)
        request.session["line_user_id"] = line_user_id
        return redirect("friendsite_social_auth:line_create_account")
    
    serialized = get_user_auth_token(**data_dict)
    user = User.objects.get(pk=int(serialized.data["user_id"]))
    login_user(request, user)
    return redirect("friendship:receiver_landing")


def line_create_account(request):
    render(request, "friendsite_social_auth/line_create_account/", {})


def line_register_process(request):
    try:
        data_dict = {x: v for x, v in request.data.items()}
        data_dict.update({x: v for x, v in request.session.items()})
        data_dict["social_auth"] = "line"
        del request.session['line_user_id']
        user = create_user(**data_dict)
        login_user(request, user)
    except (KeyError, ValueError):
        return render(request, 'friendship/register.html', {})
