from django.db import models
from django.contrib.auth.models import User

import enum
import functools
import datetime


def forDjango(cls):
    cls.do_not_call_in_templates = True
    return cls


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

        def __str__(self):
            if self == self.TRAVELER:
                return "traveler"
            elif self == self.FLIGHT_ATTENDANT:
                return "flight attendant"
            elif self == self.SHIPPING_COMPANY:
                return "shipping company"
            elif self == self.FRIENDSHIP_BIDDER:
                return "friendship bidder"
            else:
                return "other"


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

    name = models.CharField(max_length=200, null=True, blank=True,)
    phone_number = models.CharField(max_length=50, null=True, blank=True,)
    email = models.CharField(max_length=200, null=True, blank=True)
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
    name = models.CharField(max_length=200, null=True, blank=True)
    address_line_1 = models.CharField(max_length=300)
    address_line_2 = models.CharField(max_length=300, null=True, blank=True)
    address_line_3 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=300)
    region = models.CharField(max_length=300)
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=120)
    
    # Each shipping address should have an associated phone number.
    phone = models.CharField(max_length=50, null=True, blank=True)

    @enum.unique
    class AddressType(enum.IntEnum):
        RECEIVER_ADDRESS = 0
        SENDER_ADDRESS = 1

        def __str__(self):
            if self == self.RECEIVER_ADDRESS:
                return "receiver address"
            elif self == self.SENDER_ADDRESS:
                return "sender address"
            else:
                return "other"

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

        def __str__(self):
            if self == self.SHOES:
                return "shoes"
            elif self == self.OTHER:
                return "other"
            else:
                return "other"

    choices = [(x.value, x.name.title()) for x in MerchandiseType]
    choices.insert(0, (-1, "Category - please choose one"))

    url = models.URLField()
    merchandise_type = models.IntegerField(
        default=-1,
        choices=choices,
    )
    # When the receiver places a request
    date_placed = models.DateTimeField(auto_now_add=True)
    bid_end_datetime = models.DateTimeField()

    description = models.TextField(
        null=True,
        blank=True,
    )
    quantity = models.IntegerField()
    size = models.CharField(max_length=120, null=True, blank=True,)
    color = models.CharField(max_length=120, null=True, blank=True,)
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
    final_bid = models.ForeignKey(
        'Bid',
        related_name="my_order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    latest_action = models.ForeignKey(
        'OrderAction',
        related_name="my_order_action",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


class TrackingNumber(models.Model):
    @enum.unique
    class ShippingStage(enum.IntEnum):
        OTHER = -1
        MERCHANT_TO_SHIPPER = 0
        SHIPPER_TO_THAILAND_DOMESTIC = 1
        DOMESTIC_TO_RECEIVER = 2

        def __str__(self):
            if self == self.MERCHANT_TO_SHIPPER:
                return "in route to shipper"
            elif self == self.SHIPPER_TO_THAILAND_DOMESTIC:
                return "in route to thailand"
            elif self == self.DOMESTIC_TO_RECEIVER:
                return "in route to receiver"
            elif self == self.OTHER:
                return "other"
            else:
                return "other"

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name="tracking_number",
        null=True,
        blank=True,
    )

    provider = models.CharField(max_length=100, null=True, blank=True)
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

        def __str__(self):
            if self == self.CREDIT_CARD:
                return "credit card"
            elif self == self.ONLINE_WIRE_TRANSFER:
                return "online wire transfer"
            elif self == self.MANUAL_WIRE_TRANSFER:
                return "manual wire transfer"
            elif self == self.OTHER:
                return "other"
            else:
                return "other"

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name="payment_actions",
        null=True,
        blank=True,
    )

    payment_type = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in PaymentType)
    )

    account_number = models.CharField(max_length=100)


class OrderAction(models.Model):
    """
    Keeps track of the actions that were made for each order until fulfillment.
    """
    @forDjango
    @enum.unique
    class Action(enum.IntEnum):
        OTHER_ACTION = -1
        ORDER_PLACED = 100
        MATCH_FOUND = 200
        PRICE_ACCEPTED = 300
        BANKNOTE_UPLOADED = 400
        PAYMENT_RECEIVED = 500
        ITEM_ORDERED_BY_FRIENDSHIPS = 600
        ITEM_SHIPPED_BY_MERCHANT = 700
        ITEM_RECEIVED_BY_SHIPPER = 800
        ITEM_IN_TRANSIT_BY_SHIPPER = 900
        ITEM_ARRIVED_IN_THAILAND = 950
        ITEM_SHIPPED_DOMESTICALLY_BY_SHIPPER = 1000
        ORDER_FULFILLED = 1100
        ORDER_DECLINED = 1200
        ORDER_CLOSED = 1300

        def __str__(self):
            if self == self.OTHER_ACTION:
                return "other action"
            elif self == self.ORDER_PLACED:
                return "order placed"
            elif self == self.MATCH_FOUND:
                return "match_found"
            elif self == self.PRICE_ACCEPTED:
                return "price accepted"
            elif self == self.BANKNOTE_UPLOADED:
                return "banknote uploaded"
            elif self == self.PAYMENT_RECEIVED:
                return "payment received"
            elif self == self.ITEM_SHIPPED_BY_MERCHANT:
                return "item shipped by merchant"
            elif self == self.ITEM_RECEIVED_BY_SHIPPER:
                return "item received by shipper"
            elif self == self.ITEM_IN_TRANSIT_BY_SHIPPER:
                return "item left origin"
            elif self == self.ITEM_SHIPPED_DOMESTICALLY_BY_SHIPPER:
                return "item shipped domestically"
            elif self == self.ORDER_FULFILLED:
                return "order fulfilled"
            elif self == self.ORDER_DECLINED:
                return "order declined"
            elif self == self.ORDER_CLOSED:
                return "order closed"
            elif self == self.OTHER:
                return "other"
            else:
                return "other"

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    action = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in Action)
    )
    date_placed = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=1000, null=True, blank=True)


class Bid(models.Model):
    """
    When a potential shipper places a bid, it goes in this database.
    """
    def get_total(self):
        return self.wages + self.retail_price + self.import_tax + self.domestic_shipping

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
        blank=True,
    )
    transaction = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
    )
    content = models.CharField(max_length=5000)
