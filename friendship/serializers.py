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


class ShippingAddressSerializer(serializers.ModelSerializer):
	class Meta:
		model = ShippingAddress
		fields = ('id', 'user', 'address', 'phone', 'address_type', 'primary')
		read_only_fields = ('id',)


class OrderActionSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrderAction
		fields = ('id', 'order', 'action', 'date_placed', 'text')
		read_only_fields = ('id',)


class BidSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bid
		fields = ('id', 'bid_shipper', 'order', 'date_placed', 'bid_amount')
		read_only_fields = ('id',)


class ImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Image
		fields = ('id', 'date_uploaded', 'user', 'order', 'image', 'mimetype', 'image_type')
		read_only_fields = ('id',)


class OrderSerializer(serializers.ModelSerializer):
	shipper_address = ShippingAddressSerializer(read_only=True)
	receiver_address = ShippingAddressSerializer(read_only=True)
	actions = OrderActionSerializer(many=True, read_only=True)
	order_images = ImageSerializer(many=True)
	bids = BidSerializer(many=True)

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
			'order_images',
			'bids',
		)
		read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = (
			'id',
			'email',
			'first_name',
			'last_name',
			'receiver_orders',
			'shipper_orders',
			'shipping_addresses',
		)
		read_only_fields = ('id',)


class MessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Message
		fields = (
			'id',
			'date_sent',
			'transaction',
			'content',
		)
		read_only_fields = ('id',)


class TokenSerializer(serializers.ModelSerializer):
	class Meta:
		model = Token
		fields = (
			'user_id',
			'key',
		)
		read_only_fields = ('user_id', 'key')
