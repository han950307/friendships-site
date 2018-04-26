"""friendsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.models import (
	User
)
from django.urls import include, path, re_path
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView, RedirectView
from rest_framework import routers, serializers, viewsets
from friendsite import settings


# Serializers for API
class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('url', 'username', 'email', 'is_staff')


# ViewSets
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer


# Routers
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('social_auth/', include('friendsite_social_auth.urls', namespace='friendsite_social_auths')),
    path('api/', include('api.urls', namespace="api")),
    path('', include('friendship.urls', namespace="friendship")),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('marketing/', include('marketing_manager.urls', namespace='marketing_manager')),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]
