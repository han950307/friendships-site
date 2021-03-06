from django.urls import path, re_path
from . import views

app_name = 'api'
urlpatterns = [    
    path('user/<int:pk>', views.UserDetail.as_view(), name="user_data"),
    path('order/<int:pk>', views.OrderDetail.as_view(), name="order_data"),
    path('orderaction/<int:pk>', views.OrderActionDetail.as_view(), name="order_action_data"),
    path('shippingaddress/<int:pk>', views.ShippingAddressDetail.as_view(), name="shipping_address_data"),
    path('bid/<int:pk>', views.BidDetail.as_view(), name="bid_data"),
    path('message/<int:pk>', views.MessageDetail.as_view(), name="message_data"),
    path('upload_item_image/<int:order_id>', views.upload_item_image, name="upload_item_image"),

    path('request_auth_token/', views.request_auth_token, name="request_auth_token"),
    path('accounts/create_user/', views.CreateUser.as_view(), name="create_user"),

    path('submit_order', views.CreateOrder.as_view(), name="create_order"),
]
