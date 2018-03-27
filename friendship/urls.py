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
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'friendship'
urlpatterns = [
    path('', views.index, name='index'),
    # path('', views.IndexView.as_view(), name='index'),
    # path('<int:id>/', views.details, name='details'),

    # Account views
    path('register/', views.register, name='register'),
    path('register_process/', views.register_process, name='register_process'),
    path('login/', views.login_view, name='login'),
    path('login_process/', views.login_process, name='login_process'),
    path('logout/', views.logout_view, name='logout'),

    # Receiver views
    path('receiver_landing/', views.receiver_landing_view, name='receiver_landing'),
    path('place_order_process/', views.place_order_process, name='place_order_process'),
    path('order_details/<int:pk>', views.order_details, name='order_details'),
    path('upload_picture/<int:order_id>', views.upload_picture_view, name='upload_picture_view'),
    path('upload_picture_process/<int:order_id>', views.upload_picture_process, name='upload_picture_process'),

    # Sender views
    path('open_orders/<str:filter>', views.open_orders, name='open_orders'),
    path('make_bid/<int:order_id>', views.make_bid, name='make_bid'),
    path('make_bid_process/<int:order_id>', views.make_bid_process, name='make_bid_process'),

    # API Views
    path('users/', views.UserList.as_view(), name="list_users"),
    path('users/<int:pk>', views.UserDetail.as_view(), name="get_user_data"),

    # Other views
    path('testing/', views.testing, name='testing'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
