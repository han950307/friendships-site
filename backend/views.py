from django.contrib.auth.models import User
from django.contrib.messages import error
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.authtoken.models import Token
from rest_framework import (
    status,
    permissions,
    authentication,
    generics,
)

from friendsite.settings import (
    FACEBOOK_ACCESS_TOKEN,
    LINE_CLIENT_ID,
)

from api.models import LineUser
from friendship.models import (
    ShipperInfo,
    ShippingAddress,
    Order,
    OrderAction,
    Bid,
    Message,
)
from friendship.serializers import (
    UserSerializer,
    TokenSerializer,
)

import requests
import json
import datetime
import pytz
import re
import random

INCOMPLETE_DATA_MSG = "Not all required data was passed in."
USER_NOT_FOUND_MSG = "This user was not found matching the credentials. Perhaps need to register?"
BAD_DATA_MSG = "Data passed in was bad."


# BACKEND DOESNT RENDER ANYTHING!

### ACCOUNT FUNCTIONS ###
def create_line_user(user, **kwargs):
    try:
        user_id = kwargs['line_user_id']
        if type(user_id) != str:
            user_id = user_id.decode("utf-8")
    except KeyError:
        raise KeyError(INCOMPLETE_DATA_MSG)
    LineUser.objects.create(
        user=user,
        line_user_id=user_id,
    )


def create_user(**kwargs):
    """
    Process registration and put user data into the database.
    """
    # Trying to get the items.
    try:
        firstname = kwargs['first_name']
        lastname = kwargs['last_name']
        email = kwargs['email']

        if 'social_auth' in kwargs:
            social_auth = kwargs["social_auth"]

            # for none, use password.
            if social_auth == "none":
                password = kwargs['password']
            else:
                password = "".join([
                    random.choice("abcdefghijklmnopqrstuvwxyz0123456789")
                    for _
                    in range(12)
                ])

    except KeyError:
        error(request, INCOMPLETE_DATA_MSG)
        raise KeyError(INCOMPLETE_DATA_MSG)
    else:
        # Check whether this email exists in the database already.
        obj = User.objects.filter(username=email)
        if obj:
            msg = 'The email \'{}\' is already registered.'.format(email)
            raise ValueError(msg)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname,
        )

    if 'social_auth' in kwargs and social_auth == "line":
        create_line_user(user, **kwargs)

    return user


def login_user(request, user):
    login(request, user)

    # check if the user is a shipper.
    user = ShipperInfo.objects.filter(user=user)
    if user:
        print(user)
    if user and user[0].verified == True:
        request.session["is_shipper"] = True
    else:
        request.session["is_shipper"] = False


def login_user_web(request, **kwargs):
    try:
        email = kwargs['email']
        password = kwargs['password']
        print(kwargs)
    except KeyError:
        error(request, INCOMPLETE_DATA_MSG)
        raise KeyError(INCOMPLETE_DATA_MSG)     
    else:
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login_user(request, user)
        else:
            error(request, USER_NOT_FOUND_MSG)
            raise ValueError(USER_NOT_FOUND_MSG)


### ORDER RELATED FUNCTIONS ###
def create_order(**kwargs):
    if "estimated_weight" not in kwargs:
        estimated_weight = 0
    else:
        estimated_weight = kwargs["estimated_weight"]

    order = Order.objects.create(**kwargs["data"])

    action = OrderAction.objects.create(
        order=order,
        action=OrderAction.Action.ORDER_PLACED,
    )
    order.latest_action = action
    order.save()

    return order


### API SPECIFIC FUNCTIONS ###
def line_auth_token_is_valid(**kwargs):
    """
    Assumes the kwargs is formatted correctly.
    Checks token issued by line.
    """
    user_token = kwargs["user_token"]

    request_url = "https://api.line.me/v2/oauth/verify"
    response = requests.post(request_url, {'access_token': user_token})
    response_dict = json.loads(response.content)

    # if response is good, check whether client is
    if response.status_code == status.HTTP_200_OK:
        client_id = str(response_dict["client_id"])
        if client_id != LINE_CLIENT_ID:
            raise ValueError("This user needs to give permission to use friendship.")
        return True, response_dict
    else:
        return False, response_dict


def facebook_auth_token_is_valid(**kwargs):
    """
    Checks token issued by facebook.
    """
    user_token = kwargs["user_token"]
 
    request_url = "https://graph.facebook.com/debug_token?" + \
                "input_token={}&access_token={}" \
                .format(
                    requests.utils.quote(user_token),
                    requests.utils.quote(FACEBOOK_ACCESS_TOKEN)
                )

    response = requests.get(request_url)
    response_dict = json.loads(response.content)

    if (response.status_code == status.HTTP_200_OK) and response_dict["data"]["is_valid"]:
        return True, response_dict
    else:
        return False, response_dict


def verify_social_auth_token(**kwargs):
    try:
        social_auth = kwargs["social_auth"]
        user_token = kwargs["user_token"]
        if social_auth == "line":
            user_id = kwargs["line_user_id"]
            return line_auth_token_is_valid(**kwargs)
        elif social_auth == "facebook":
            email = kwargs["email"]
            return facebook_auth_token_is_valid(**kwargs)
        elif social_auth == "none":
            return True, _
        else:
            raise ValueError(BAD_DATA_MSG)
    except KeyError:
        raise KeyError(INCOMPLETE_DATA_MSG)


def make_token_for_user(user):
    """
    Makes token for user
    """
    queryset = Token.objects.filter(user=user)
    if queryset:
        token = queryset[0]
    else:
        token = Token.objects.create(user=user)
    serialized = TokenSerializer(token)
    return serialized


def get_user_auth_token(**kwargs):
    """
    Returns the serialized version of user token.
    """
    valid, response_dict = verify_social_auth_token(**kwargs)
    if not valid:
        raise ValueError("Social auth token validation failed. JSONDUMPS {}".format(
            json.dumps(response_dict)
        ))

    # Doesn't need try/except because this is checked in verify_social_auth_token.
    social_auth = kwargs["social_auth"]

    if social_auth == "line":
        user_id = kwargs["line_user_id"]
        queryset = LineUser.objects.filter(line_user_id=user_id)

        if not queryset:
            raise ValueError(USER_NOT_FOUND_MSG)
        else:
            user = queryset[0].user
    elif social_auth == "facebook":
        email = kwargs["email"]
        queryset = User.objects.filter(email=email)
        if not queryset:
            raise ValueError(USER_NOT_FOUND_MSG)
        else:
            user = queryset[0]
    else:
        raise ValueError(BAD_DATA_MSG)

    return make_token_for_user(user)
