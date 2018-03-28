from django.db.utils import IntegrityError
from django.contrib.auth.models import User

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

from friendship.models import (
    ShipperList,
    ShippingAddress,
    Order,
    OrderAction,
    Bid,
    Image,
    Message,
    LineUser,
)

from friendsite.settings import (
	ACCESS_TOKEN_FACEBOOK,
	CLIENT_ID_LINE,
)
from friendship.serializers import (
	UserSerializer,
	TokenSerializer,
	OrderSerializer,
	OrderActionSerializer,
	ShippingAddressSerializer,
	BidSerializer,
	ImageSerializer,
	MessageSerializer,
)

import requests
import json
import random


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


class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Image.objects.all()
	serializer_class = ImageSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	permission_classes = (permissions.IsAuthenticated,)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Message.objects.all()
	serializer_class = MessageSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	permission_classes = (permissions.IsAuthenticated,)


def make_token_for_user(request, user):
	queryset = Token.objects.filter(user=user)
	if queryset:
		token = queryset[0]
	else:
		token = Token.objects.create(user=user)
	serialized = TokenSerializer(token)
	return Response(
		serialized.data,
		status=status.HTTP_200_OK,
	)


def auth_token_line_is_valid(request):
	try:
		if request.method == "POST":
			user_token = request.data["user_token"]
			social_auth = request.data["social_auth"]
			user_id = request.data["user_id"]
		if request.method == "GET":
			user_token = request.GET["user_token"]
			social_auth = request.GET["social_auth"]
			user_id = request.GET["user_id"]
	except KeyError:
			return Response(
				{"message": "All the fields have to be filled out"},
				status=status.HTTP_400_BAD_REQUEST,
			)
	request_str = "https://api.line.me/oauth2/v2.1/token?" + \
				"input_token={}" \
				.format(
					requests.utils.quote(user_token)
				)
	response = requests.get(request_str)
	response_dict = json.loads(response.content)

	if response.status_code == status.HTTP_200_OK:
		return True
	else:
		return False


def request_auth_token_line(request):
	if auth_token_line_is_valid(request):
		request_str = "https://api.line.me/oauth2/v2.1/token?" + \
					"input_token={}" \
					.format(
						requests.utils.quote(user_token)
					)
		if request.method == "POST":
			user_id = request.data["user_id"]
		if request.method == "GET":
			user_id = request.GET["user_id"]

		response = requests.get(request_str)
		response_dict = json.loads(response.content)

		queryset = None
		client_id = str(response_dict["client_id"])
		if client_id != CLIENT_ID_LINE:
			return Response(
				{
					"message": "This user is not approved to be used for this application.",
					"data_from_social_auth": response_dict,
				},
				status=status.HTTP_400_BAD_REQUEST,
			)
		else:
			queryset = LineUser.objects.filter(line_user_id=user_id)

		# raise 404 if the user is not found with the email.
		if not queryset:
			return Response(
				{
					"message": "The user is not yet registered. Please register" + \
					"the user first using /api/register"
				},
				status=status.HTTP_404_NOT_FOUND,
			)

		# if the user exists, then make a token and return it for that user.
		line_user = queryset[0]
		user = line_user.user
		return make_token_for_user(request, user)
	# Auth key was wrong or something.
	else:
		return Response(
			{
				"message": "User auth key was invalid or bad.",
				"data_from_social_auth": response_dict,
			},
			status=status.HTTP_400_BAD_REQUEST,
		)


def auth_token_facebook_is_valid(request):
	try:
		if request.method == "POST":
			user_token = request.data["user_token"]
			email = request.data["email"]
		if request.method == "GET":
			user_token = request.GET["user_token"]
			email = request.GET["email"]
	except KeyError:
			return Response(
				{"message": "All the fields have to be filled out"},
				status=status.HTTP_400_BAD_REQUEST,
			)
	request_str = "https://graph.facebook.com/debug_token?" + \
				"input_token={}&access_token={}" \
				.format(
					requests.utils.quote(user_token),
					requests.utils.quote(ACCESS_TOKEN_FACEBOOK)
				)

	response = requests.get(request_str)
	response_dict = json.loads(response.content)

	# Do this if user_auth_token is valid
	if (response.status_code == status.HTTP_200_OK) and response_dict["data"]["is_valid"]:
		return True
	else:
		return False


def request_auth_token_facebook(request):
	if auth_token_facebook_is_valid(request):
		if request.method == "POST":
			email = request.data["email"]
		if request.method == "GET":
			email = request.GET["email"]
		queryset = User.objects.filter(email=email)
		
		# raise 404 if the user is not found with the email.
		if not queryset:
			return Response(
				{
					"message": "The user is not yet registered. Please register" + \
					"the user first using /api/register"
				},
				status=status.HTTP_404_NOT_FOUND,
			)

		# if the user exists, then make a token and return it for that user.
		user = queryset[0]
		return make_token_for_user(request, user)
	# Auth key was wrong or something.
	else:
		return Response(
			{
				"message": "User auth key was invalid or bad.",
				"data_from_social_auth": response_dict,
			},
			status=status.HTTP_400_BAD_REQUEST,
		)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def request_auth_token(request):
	if request.method == 'GET':
		try:
			social_auth = request.GET["social_auth"]
		except KeyError:
			return Response(
				{
					"message": "Invalid parameters.",
				},
				status=status.HTTP_400_BAD_REQUEST,
			)
		if (social_auth == "facebook"):
			return request_auth_token_facebook(request)
		elif (social_auth == "line"):
			return request_auth_token_line(request)


class CreateUser(generics.CreateAPIView):
	model = User
	serializer_class = UserSerializer
	permission_classes = (permissions.AllowAny,)
	throttle_classes = (AnonRateThrottle,)

	def create(self, request):
		serialized = UserSerializer(data=request.data)
		# need the social auth
		try:
			social_auth = request.data['social_auth']
		except KeyError:
			return Response(
				{"message": "All the fields have to be filled out"},
				status=status.HTTP_400_BAD_REQUEST,
			)


		# make sure auth tokens are valid for social auth.
		token_valid = False
		if social_auth == "facebook":
			token_valid = auth_token_facebook_is_valid(request)
		elif social_auth == "line":
			token_valid = auth_token_line_is_valid(request)
		elif social_auth == "none":
			token_valid = True

		if not token_valid:
			return Response(
				{
					"message": "User auth key was invalid or bad.",
					"data_from_social_auth": response_dict,
				},
				status=status.HTTP_400_BAD_REQUEST,
			)

		# return bad request response if it's not valid.
		if serialized.is_valid():
			email = serialized.data['email']
			username = serialized.data['email']
			firstname = serialized.data['first_name']
			lastname = serialized.data['last_name']
		else:
			return Response(
				{"message": "The data is invalid."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		# is a passord present?
		try:
			password = request.data['password']
		# if no pass, then generate a random pass and let user change it later if need to.
		except KeyError:
			password = "".join([
				random.choice("abcdefghijklmnopqrstuvwxyz0123456789")
				for _
				in range(12)
			])

		# Try to create user.
		try:
			user = User.objects.create_user(
				username,
				email,
				password
			)
		except IntegrityError:
			return Response(
				{"message": "The email {} is already registered".format(email)},
				status=status.HTTP_400_BAD_REQUEST,
			)
		user.first_name = firstname
		user.last_name = lastname
		user.save()

		if social_auth == "line":
			try:
				user_id = request.data['user_id']
				if type(user_id) != str:
					user_id = user_id.decode("utf-8")
			except KeyError:
				return Response(
					{"message": "All of the required fields for line have to be filled out."},
					status=status.HTTP_400_BAD_REQUEST,
				)
			LineUser.objects.create(
				user=user,
				line_user_id=user_id,
			)

		return Response(
			status=status.HTTP_201_CREATED
		)
