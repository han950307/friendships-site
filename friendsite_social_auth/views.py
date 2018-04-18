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
    create_line_user,
)

import json
import requests
import hashlib
import re
import hmac

from urllib.parse import quote


class SocialLoginView(View):
    base_url = None
    client_id = None
    redirect_uri = None
    response_type = "code"
    state = "yayimalive"

    def oauth_request_auth_code(self, next_page):
        url = self.base_url + "?" + \
               "client_id=" + quote(self.client_id) + \
               "&response_type=" + quote(self.response_type) + \
               "&redirect_uri=" + quote(self.redirect_uri) + \
               "&state=" + quote(next_page)

        return redirect(url)

    def get(self, request):
        if "next" in request.session:
            next_page = "nextpageaddress" + request.session["next"]
        else:
            next_page = self.state
        return self.oauth_request_auth_code(next_page)


class FacebookSocialLoginView(SocialLoginView):
    base_url = "https://www." + settings.FACEBOOK_API_URL + "/dialog/oauth"
    client_id = settings.FACEBOOK_CLIENT_ID
    redirect_uri = settings.FACEBOOK_REDIRECT_URI

    def get(self, request):
        return super().get(request)


class LineSocialLoginView(SocialLoginView):
    base_url = settings.LINE_AUTH_URL
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
    """
    Interesting thing is if you register as line or any other method,
    You automatically register as facebook too. Basically
    if you have an email on our server you can login through facebook.
    """
    try:
        code = request.GET["code"]
        state = request.GET["state"]
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
        data_dict['facebook_user_id'] = user_id

        # if user token exists, that means they authorized with them.
        try:
            serialized = get_user_auth_token(**data_dict)
        except ValueError:
            # Sometimes email doesn't exist, then must verify.
            if 'email' not in data_dict:
                request.session["facebook_user_id"] = user_id
                return redirect("friendsite_social_auth:line_create_account", social_auth="Facebook")
            user = create_user(**data_dict)
            serialized = get_user_auth_token(**data_dict)

        user = User.objects.get(pk=int(serialized.data["user_id"]))
        login_user(request, user)
    else:
        error(request, "Failed logging into facebook. Please try again.")
        return redirect("friendship:index")

    print(state)
    if state.startswith("nextpageaddress"):
        next_page = re.sub("nextpageaddress", "", state)
        return redirect(next_page)
    return redirect("friendship:receiver_landing")


def line_callback(request):
    try:
        code = request.GET["code"]
        state = request.GET["state"]
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
        return redirect("friendship:login")

    ## NOW GET USER ID!
    header_dict = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    request_url = "https://api.line.me/v2/profile"
    response = requests.get(request_url, headers=header_dict)
    response_dict = json.loads(response.content)
    try:
        user_id = response_dict['userId']
    except KeyError:
        error(request, "Line login failed" + str(response_dict))
        return redirect("friendship:login")

    # Login user if already exists. else, create user then login.
    data_dict = {x: v for x, v in response_dict.items()}
    data_dict['social_auth'] = 'line'
    data_dict['user_token'] = access_token
    data_dict['line_user_id'] = user_id

    # if user token exists, that means they authorized with them.
    try:
        serialized = get_user_auth_token(**data_dict)
    except ValueError:
        request.session["line_user_id"] = user_id
        return redirect("friendsite_social_auth:line_create_account", social_auth="Line")
    
    serialized = get_user_auth_token(**data_dict)
    user = User.objects.get(pk=int(serialized.data["user_id"]))
    login_user(request, user)

    print(state)
    if state.startswith("nextpageaddress"):
        next_page = re.sub("nextpageaddress", "", state)
        return redirect(next_page)
    return redirect("friendship:receiver_landing")


def line_create_account(request, social_auth):
    return render(request, "friendsite_social_auth/line_create_user.html", {
        'user': None,
        'social_auth': social_auth.title(),
    })


def line_register_process(request):
    try:
        data_dict = {x: v for x, v in request.POST.items()}
        data_dict.update({x: v for x, v in request.session.items()})
        data_dict["social_auth"] = data_dict["social_auth"].lower()

        # If email already exists in the database, then this is executed.
        if 'confirm' in data_dict:
            # If user already exists, then just create the line user.
            if data_dict["confirm"] == "True":
                user = User.objects.filter(username=data_dict["email"])[0]
                create_line_user(user, **data_dict)
            else:
                error(request, "Please double check your account. Perhaps you already have an account?")
                return redirect("friendship:login")
        # If the email does not already exist in the database, then do this.
        # This tries to create user
        else:
            try:
                user = create_user(**data_dict)
            # This error gets raised when email already exists. Ask users for
            # additional info.
            except ValueError:
                user = User.objects.filter(username=data_dict["email"])[0]
                request.session.update({x: v for x, v in request.POST.items()})
                return render(request, "friendsite_social_auth/line_create_user.html", {
                    'user': user,
                    'social_auth': data_dict['social_auth'].title()
                })
        for key in list(request.session.keys()):
            del request.session[key]
        login_user(request, user)
    except (KeyError, ValueError) as e:
        print(e)
        return render(request, 'friendship/register.html', {})

    return redirect('friendship:receiver_landing')
