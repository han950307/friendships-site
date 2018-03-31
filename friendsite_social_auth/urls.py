from django.urls import path, re_path
from . import views

app_name = 'friendsite_social_auth'
urlpatterns = [
	path('facebook_login/', views.facebook_login, name="facebook_login"),
    path('facebook_callback/', views.facebook_callback, name="facebook_callback"),
]