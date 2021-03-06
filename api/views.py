from django.shortcuts import render
from django.db.utils import IntegrityError
from django.contrib.messages import error
from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.throttling import (
    AnonRateThrottle,
    UserRateThrottle,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import (
    status,
    permissions,
    authentication,
    generics,
)

from friendship.models import (
    ShipperInfo,
    ShippingAddress,
    Order,
    OrderAction,
    Bid,
    Message,
)

from friendsite_social_auth.models import LineUser

from friendship.serializers import (
    UserSerializer,
    TokenSerializer,
    OrderSerializer,
    OrderActionSerializer,
    ShippingAddressSerializer,
    BidSerializer,
    MessageSerializer,
)

from friendsite import settings

from backend.views import (
    get_user_auth_token,
    verify_social_auth_token,
    create_user,
)

import requests
import json
import random
import base64
import hashlib
import hmac
import time
import braintree


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class ShippingAddressDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class OrderActionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderAction.objects.all()
    serializer_class = OrderActionSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class BidDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def request_auth_token(request):
    if request.method == 'GET':
        data_dict = {x: v for x, v in request.GET.items()}
        try:
            serialized_token = get_user_auth_token(**data_dict)
        except KeyError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

    return Response(
        serialized_token.data,
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
def upload_item_image(request, order_id):
    order = Order.objects.filter(pk=order_id)
    if not order:
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )
    else:
        order = order[0]

    if order.receiver != request.user and order.shipper != request.user:
        return Response(
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'POST':
        files = request.FILES

        if len(files) > 0:
            file = files[0]
            order.item_image = file
            order.save()

            return Response(
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                status=status.HTTP_400_NOT_FOUND,
            )
    else:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
        )


class CreateUser(generics.CreateAPIView):
    model = User
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (AnonRateThrottle,)

    def create(self, request):
        serialized = UserSerializer(data=request.data)
        if (serialized.is_valid()):
            data_dict = {x: v for x, v in serialized.data.items()}
            data_dict.update({x: v for x, v in request.data.items()})
        else:
            return Response(
                {"error": "Input data was bad. DATA DUMP {}".format(str(request.data))},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # make sure auth tokens are valid for social auth.
        try:
            valid, response_dict = verify_social_auth_token(**data_dict)
        except (ValueError, KeyError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # only do this if valid.
        if valid:
            try:
                create_user(**data_dict)
            except ValueError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "error": "Social auth token validation failed. JSONDUMPS {}" \
                        .format(json.dumps(response_dict)),
                    "error_msg": serialized.errors,
                    },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            status=status.HTTP_201_CREATED
        )


class CreateOrder(generics.CreateAPIView):
    model = Order
    serializer_class = OrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = (UserRateThrottle,)

    