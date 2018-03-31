from django.urls import path, re_path
from . import views

app_name = 'friendsite_social_auth'
urlpatterns = [
    path('facebook_login/', views.FacebookSocialLoginView.as_view(), name="facebook_login"),
    path('facebook_callback/', views.facebook_callback, name="facebook_callback"),
    path('line_login/', views.LineSocialLoginView.as_view(), name="line_login"),
    path('line_callback/', views.line_callback, name="line_callback"),
    path('line_create_account/', views.line_callback, name="line_create_account"),
]
