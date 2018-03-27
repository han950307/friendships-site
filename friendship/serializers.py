from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import (
    User,
)
from friendship.models import (
    ShipperList,
    ShippingAddress,
    Order,
    OrderAction,
    Bid,
    Image,
    Message,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class ShippingAddressSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)

	class Meta:
		model = ShippingAddress
		fields = ('id', 'user', 'address', 'phone', 'address_type', 'primary')


class OrderActionSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrderAction
		fields = ('id', 'order', 'action', 'date_placed', 'text')


class BidSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bid
		fields = ('id', 'bid_shipper', 'order', 'date_placed', 'bid_amount')


class ImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Image
		fields = ('id', 'date_uploaded', 'user', 'order', 'image', 'mimetype', 'image_type')


class OrderSerializer(serializers.ModelSerializer):
	shipper = UserSerializer(read_only=True)
	shipper_address = ShippingAddressSerializer(read_only=True)
	receiver = UserSerializer(read_only=True)
	receiver_address = ShippingAddressSerializer(read_only=True)
	actions = OrderActionSerializer(many=True, read_only=True)

	class Meta:
		model = Order
		fields = (
			'id',
			'url',
			'merchandise_type',
			'date_placed',
			'bid_end_datetime',
			'description',
			'quantity',
			'shipper',
			'shipper_address',
			'receiver',
			'receiver_address',
			'actions',
		)


class MessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Message
		fields = (
			'id',
			'date_sent',
			'transaction',
			'content',
		)


class TokenSerializer(serializers.ModelSerializer):
	class Meta:
		model = Token
		fields = (
			'user_id',
			'key',
		)
