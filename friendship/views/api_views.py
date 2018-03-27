from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import (
	status,
	permissions,
	authentication,
	generics,
)
from friendship.models import User
from friendship.serializers import UserSerializer


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
