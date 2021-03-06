from django.contrib.auth.models import User
from django.contrib.messages import error
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.shortcuts import (
    render,
)
from django.core.files.base import ContentFile
from django.core import mail
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
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from friendsite.settings import (
    FACEBOOK_ACCESS_TOKEN,
    LINE_CLIENT_ID,
)

from friendsite import settings

from friendsite_social_auth.models import LineUser, FacebookUser
import friendship
from friendship.models import (
    ShipperInfo,
    ShippingAddress,
    Order,
    OrderAction,
    Money,
    Bid,
    Message,
)
from friendship.serializers import (
    UserSerializer,
    TokenSerializer,
)
from friendship.backends import (RandomFileName)

import requests
import json
import math
import datetime
import pytz
import decimal
import re
import random

INCOMPLETE_DATA_MSG = "Not all required data was passed in."
USER_NOT_FOUND_MSG = "This user was not found matching the credentials. Perhaps need to register?"
BAD_DATA_MSG = "Data passed in was bad."


# BACKEND DOESNT RENDER ANYTHING!
def send_order_created_email(order):
    """
    Temporary function to notify army and hansung when each order is created.
    """
    body = "yo an order got created"

    # Only send for prod bc we dont care about testing in local.
    if not settings.DEBUG:
        mail.send_mail(
            "Order #{} Created by {} {}".format(order.id, order.receiver.first_name, order.receiver.last_name),
            body,
            "FriendShips <no-reply@friendships.link>",
            ["nt62@duke.edu", "h.k@duke.edu"],
            fail_silently=False,
        )


def send_bid_email(order):
    """
    Send an email for this order.
    """
    body = "Dear {first_name},\n\nYou have your first bid on your item" + \
            "! Please visit {url} to view."

    body_str = body.format(
        first_name=order.receiver.first_name,
        url="https://www.friendships.link/order_details/{}".format(order.id),
    )

    if not settings.LOCAL:
        mail.send_mail(
            "First Bid on Order #{}".format(order.id),
            body_str,
            "FriendShips <no-reply@friendships.link>",
            [order.receiver.email],
            fail_silently=False,
        )


def create_money_object(key, **kwargs):
    if key in kwargs:
        val = decimal.Decimal(kwargs[key])
        return Money.objects.create(value=val, currency=kwargs["currency"])
    else:
        return None


def get_cur_wage(order):
    """
    Algorithm to get the current wage for the time.
    Requires "order, "retail_price", "curerncy", "wages" (in float)
    """
    trickle_down_to_bid = Bid.objects.filter(order=order).filter(bid_trickle=True)
    min_value = trickle_down_to_bid[0].wages.get_value()
    max_add = trickle_down_to_bid[0].retail_price.get_value() * settings.BID_TRICKLE_RATIO

    date_placed = order.date_placed
    bid_end_time = order.bid_end_datetime
    bid_length = bid_end_time - date_placed

    cur_time = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    time_left = bid_end_time - cur_time

    # frac_left goes from 1 to 0 as time goes on.
    frac_left = decimal.Decimal(time_left / bid_length)

    # transformation to make bid go down quicker in the beginning.
    alpha = decimal.Decimal(math.pow(frac_left, 4))

    # Adding a random normally distributed number.
    additional = max_add * alpha
    mean = additional + min_value
    std_dev = additional / 20

    return decimal.Decimal(random.gauss(float(mean), float(std_dev)))


def make_bid_backend(shipper, order, **kwargs):
    """
    Creates a bid objects. requires "retail_price", "currency" (int),
    "wages", "bid_trickle"
    """
    kwargs["service_fee"] = decimal.Decimal(kwargs["retail_price"]) * settings.SERVICE_FEE_RATE

    bid = Bid.objects.create(
        order=order,
        shipper=shipper,
        bid_trickle=kwargs["bid_trickle"],
        wages=create_money_object("wages", **kwargs),
        retail_price=create_money_object("retail_price", **kwargs),
        service_fee=create_money_object("service_fee", **kwargs),
    )

    # "bid_trickle" signifies that this is the first bid created with min_bid as parameter.
    # So create an actual bid here. Any Bids with "bid_trickle = True" does not count as
    # an actual bid.
    if kwargs["bid_trickle"]:
        kwargs["wages"] = get_cur_wage(order)
        kwargs["bid_trickle"] = False
        make_bid_backend(shipper, order, **kwargs)

    IMAGE_FILETYPES = [
        "png",
        "jpg",
        "jpeg",
        "gif",
        "tiff",
        "bmp",
        "svg",
    ]

    # Uploading file directly from a url, if it exists
    if "item_image" in kwargs and kwargs["item_image"]:
        order.item_image = kwargs["item_image"]
        order.save()
    elif "item_image_url" in kwargs and kwargs["item_image_url"] and not order.item_image:
        item_image_url = kwargs["item_image_url"]
        response = requests.get(item_image_url)
        filetype = re.sub(r"image\/", "", response.headers["Content-Type"], flags=re.I)
        if filetype.lower() in IMAGE_FILETYPES:
            order.item_image = ContentFile(response.content)
            order.item_image.name = "blah.{}".format(filetype)
            order.save()

    if len(Bid.objects.filter(order=order).filter(bid_trickle=False)) == 1:
        send_bid_email(order)


### ACCOUNT FUNCTIONS ###
def create_line_user(user, **kwargs):
    try:
        if kwargs["social_auth"] == "line":
            user_id = kwargs['line_user_id']
        elif kwargs["social_auth"] == "facebook":
            user_id = kwargs['facebook_user_id']
        if type(user_id) != str:
            user_id = user_id.decode("utf-8")
    except KeyError:
        raise KeyError(INCOMPLETE_DATA_MSG)

    if kwargs["social_auth"] == "line":
        LineUser.objects.create(
            user=user,
            line_user_id=user_id,
        )
    elif kwargs["social_auth"] == "facebook":
        FacebookUser.objects.create(
            user=user,
            facebook_user_id=user_id,
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
    if 'social_auth' in kwargs and social_auth == "facebook":
        create_line_user(user, **kwargs)

    return user


def login_user(request, user):
    login(request, user)

    if 'locale' not in request.session:
        request.session['locale'] = 'th_TH'

    # check if the user is a shipper.
    user_list = ShipperInfo.objects.filter(user=user)
    if user_list and user_list[0].verified == True:
        request.session["is_shipper"] = True
    else:
        request.session["is_shipper"] = False


def login_user_web(request, **kwargs):
    try:
        email = kwargs['email']
        password = kwargs['password']
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
    friendship.views.create_action_for_order(order, OrderAction.Action.ORDER_PLACED)

    if not settings.LOCAL:
        send_order_created_email(order)

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
            if 'email' not in kwargs:
                user_id = kwargs['facebook_user_id']
            else:
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
        if 'email' not in kwargs:
            user_id = kwargs["facebook_user_id"]
            queryset = FacebookUser.objects.filter(facebook_user_id=user_id)
        else:
            email = kwargs["email"]
            queryset = User.objects.filter(email=email)
        if not queryset:
            raise ValueError(USER_NOT_FOUND_MSG)
        else:
            user = queryset[0] if 'email' in kwargs else queryset[0].user
    else:
        raise ValueError(BAD_DATA_MSG)

    return make_token_for_user(user)
