from django.db import models
from django.contrib.auth.models import User

import enum

import datetime


# Create your models here.
class ShipperList(models.Model):
    """
    Contains a list of shippers.
    """
    @enum.unique
    class ShipperType(enum.IntEnum):
        TRAVELER = 0
        FLIGHT_ATTENDANTS = 1
        SHIPPING_COMPANIES = 2
        FRIENDSHIP_BIDDERS = 3

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="is_shipper",
    )

    url = models.URLField()
    shipper_type = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in SihpperType)
    )


class ShippingAddress(models.Model):
    """
    Keeps track of shipping addresses for each user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shipping_addresses'
    )
    # name field associated for each shipping address. doesn't really matter.
    name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=1000)
    
    # Each shipping address should have an associated phone number.
    phone = models.CharField(max_length=50, null=True)

    @enum.unique
    class AddressType(enum.IntEnum):
        RECEIVER_ADDRESS = 0
        SENDER_ADDRESS = 1

    address_type = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in AddressType)
    )

    primary = models.BooleanField()


class Order(models.Model):
    """
    An entry gets created when a receiver places an order.
    """
    @enum.unique
    class MerchandiseType(enum.IntEnum):
        OTHER = 0
        SHOES = 1

    url = models.URLField()
    merchandise_type = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in MerchandiseType)
    )
    # When the receiver places a request
    date_placed = models.DateTimeField(auto_now_add=True)
    bid_end_datetime = models.DateTimeField()

    description = models.TextField()
    quantity = models.IntegerField()
    shipper = models.ForeignKey(
        User,
        related_name="shipper_orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    shipper_address = models.ForeignKey(
        ShippingAddress,
        related_name="shipper_address",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        User,
        related_name="receiver_orders",
        on_delete=models.CASCADE,
    )
    receiver_address = models.ForeignKey(
        ShippingAddress,
        related_name="receiver_address",
        on_delete=models.CASCADE,
    )
    estimated_weight = models.IntegerField()


class OrderAction(models.Model):
    """
    Keeps track of the actions that were made for each order until fulfillment.
    """
    @enum.unique
    class Action(enum.IntEnum):
        OTHER_ACTION = -1
        ORDER_PLACED = 0
        MATCH_FOUND = 1
        PRICE_CONFIRMED = 2
        BANKNOTE_UPLOADED = 5
        PAYMENT_RECEIVED = 3
        ORDER_FULFILLED = 4

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    action = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in Action)
    )
    date_placed = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=1000, null=True)


class Bid(models.Model):
    """
    When a potential shipper places a bid, it goes in this database.
    """
    shipper = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="bids",
    )
    date_placed = models.DateTimeField(
        auto_now_add=True,
    )
    bid_amount = models.DecimalField(max_digits=50, decimal_places=4)
    currency = models.CharField(max_length=15)


class Image(models.Model):
    date_uploaded = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_images",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_images",
    )
    image = models.TextField()
    mimetype = models.CharField(max_length=25)
    # Bank-slip or whatever
    image_type = models.IntegerField()


class Message(models.Model):
    date_sent = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    transaction = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
    )
    content = models.CharField(max_length=5000)
