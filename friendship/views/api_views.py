from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework import (
	status,
	permissions,
	authentication,
	generics,
)
from friendship.models import User
from friendsite.settings import ACCESS_TOKEN_FACEBOOK
from friendship.serializers import (
	UserSerializer,
	TokenSerializer,
)

import requests
import json


class UserList(generics.ListCreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	permission_classes = (permissions.IsAuthenticated,)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	permission_classes = (permissions.IsAuthenticated,)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def request_auth_token(request):
	if request.method == 'GET':
		user_token = request.GET["user_token"]
		email = request.GET["email"]
		social_auth = request.GET["social_auth"]

		if (social_auth == "facebook"):
			request_str = "https://graph.facebook.com/debug_token?" + \
						"input_token={}&access_token={}" \
						.format(user_token, ACCESS_TOKEN_FACEBOOK)
		else:
			request_str = "https://www.google.com"

		response = requests.get(request_str)
		response_dict = json.loads(response.content)
		print(response.content.decode('utf-8'))

		# Do this if user_auth_token is valid
		if response_dict["data"]["is_valid"] or True:
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

			# if the email exists, then make a token and return it for that user.
			user = queryset[0]
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
		# Auth key was wrong or something.
		else:
			return Response(
				{
					"message": "User auth key was not registered.",
					"data_from_social_auth": response_dict,
				},
				status=status.HTTP_400_BAD_REQUEST,
			)
