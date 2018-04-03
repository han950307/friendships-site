from django.db import models
from django.contrib.auth.models import User

import enum
import functools
import datetime


# Create your models here.
class ShipperInfo(models.Model):
    """
    Contains a list of shippers.
    """
    @enum.unique
    class ShipperType(enum.IntEnum):
        TRAVELER = 0
        FLIGHT_ATTENDANT = 1
        SHIPPING_COMPANY = 2
        FRIENDSHIP_BIDDER = 3

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="is_shipper",
    )

    url = models.URLField(null=True, blank=True)

    shipper_type = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in ShipperType)
    )
    
    id_image = models.ImageField(
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=200, null=True)
    verified = models.BooleanField(default=False)


class Flight(models.Model):
    """
    Shipper's flight info.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='flights'
    )
    confirmation_number = models.CharField(max_length=120)


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
    address_line_1 = models.CharField(max_length=300)
    address_line_2 = models.CharField(max_length=300, null=True, blank=True)
    address_line_3 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=300)
    region = models.CharField(max_length=300)
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=120)
    
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
        OTHER = -1
        SHOES = 0

    url = models.URLField()
    merchandise_type = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in MerchandiseType)
    )
    # When the receiver places a request
    date_placed = models.DateTimeField(auto_now_add=True)
    bid_end_datetime = models.DateTimeField()

    description = models.TextField()
    quantity = models.IntegerField()
    size = models.CharField(max_length=120)
    color = models.CharField(max_length=120)
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
    item_image = models.ImageField(
        null=True,
        blank=True,
    )
    banknote_image = models.ImageField(
        null=True,
        blank=True,
    )
    estimated_weight = models.IntegerField(
        default=0,
    )


class TrackingNumber(models.Model):
    @enum.unique
    class ShippingStage(enum.IntEnum):
        OTHER = -1
        MERCHANT_TO_SHIPPER = 0
        SHIPPER_TO_THAILAND_DOMESTIC = 1
        DOMESTIC_TO_RECEIVER = 2

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name="tracking_number",
        null=True,
    )

    provider = models.CharField(max_length=100, null=True)
    tracking_number = models.CharField(max_length=140)
    shipping_stage = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in ShippingStage)
    )
    url = models.URLField(null=True, blank=True)


class PaymentAction(models.Model):
    @enum.unique
    class PaymentType(enum.IntEnum):
        OTHER = -1
        CREDIT_CARD = 0
        ONLINE_WIRE_TRANSFER = 1
        MANUAL_WIRE_TRANSFER = 2

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name="payment_actions",
        null=True
    )

    account_number = models.CharField(max_length=100)


class OrderAction(models.Model):
    """
    Keeps track of the actions that were made for each order until fulfillment.
    """
    @enum.unique
    class Action(enum.IntEnum):
        OTHER_ACTION = -1
        ORDER_PLACED = 0
        MATCH_FOUND = 1
        PRICE_ACCEPTED = 2
        BANKNOTE_UPLOADED = 3
        PAYMENT_RECEIVED = 4
        ITEM_SHIPPED_BY_MERCHANT = 5
        ITEM_RECEIVED_BY_SHIPPER = 6
        ORDER_FULFILLED = 7
        ORDER_DECLINED = 8
        ORDER_CLOSED = 9

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


@functools.total_ordering
class Bid(models.Model):
    """
    When a potential shipper places a bid, it goes in this database.
    """
    def __lt__(self, other):
        this_value = self.wages + self.retail_price + self.import_tax + self.domestic_shipping
        other_value = other.wages + other.retail_price + other.import_tax + other.domestic_shipping
        return this_value < other_value

    def __eq__(self, other):
        this_value = self.wages + self.retail_price + self.import_tax + self.domestic_shipping
        other_value = other.wages + other.retail_price + other.import_tax + other.domestic_shipping
        return this_value == other_value

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
    wages = models.DecimalField(max_digits=50, decimal_places=4, default=0)
    retail_price = models.DecimalField(max_digits=50, decimal_places=4, default=0)
    import_tax = models.DecimalField(max_digits=50, decimal_places=4, default=0)
    domestic_shipping = models.DecimalField(max_digits=50, decimal_places=4, default=0)
    currency = models.CharField(max_length=15)


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
