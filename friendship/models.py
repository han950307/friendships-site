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
        PLEASE_CHOOSE = 0
        SHOES = 13
        COLLECTIBLES = 1
        FOOD_AND_DRINKS = 3
        TOYS_AND_HOBBY = 2
        ELECTRONICS_AND_ACCESSORIES = 4
        LADIES_FASHION_AND_ACCESSORIES = 5
        MENS_FASHION_AND_ACCESSORIES = 6
        SPORTS = 7
        BEAUTY_PRODUCTS = 8
        HOUSEHOLD_PRODUCTS = 9
        PET_PRODUCTS = 10
        GAMES = 11
        OTHER = 12

        def __str__(self):
            if self == self.SHOES:
                return "shoes"
            elif self == self.OTHER:
                return "other"
            elif self == self.COLLECTIBLES:
                return "collectibles"
            elif self == self.FOOD_AND_DRINKS:
                return "food & drinks"
            elif self == self.TOYS_AND_HOBBY:
                return "toys & hobby"
            elif self == self.ELECTRONICS_AND_ACCESSORIES:
                return "electronics & accessories"
            elif self == self.LADIES_FASHION_AND_ACCESSORIES:
                return "ladies fashion & accessories"
            elif self == self.MENS_FASHION_AND_ACCESSORIES:
                return "mens fashion & accessories"
            elif self == self.SPORTS:
                return "sports"
            elif self == self.BEAUTY_PRODUCTS:
                return "beauty products"
            elif self == self.HOUSEHOLD_PRODUCTS:
                return "household products"
            elif self == self.PET_PRODUCTS:
                return "pet products"
            elif self == self.GAMES:
                return "games"
            elif self == self.PLEASE_CHOOSE:
                return "choose one*"
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
        MATCH_NOT_FOUND = 50
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
                return "match found"
            elif self == self.MATCH_NOT_FOUND:
                return "match not found"
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


class Money(models.Model):
    class ExchangeRates(object):
        # XXX to YYY exchange rate.
        USD_TBT = 32.49

    @forDjango
    @enum.unique
    class Currency(enum.IntEnum):
        OTHER = -1
        USD = 50
        TBT = 100

        def __str__(self):
            if self == self.USD:
                return "usd"
            elif self == self.TBT:
                return "tbt"
            else:
                return "other"

        @classmethod
        def get_currency(cls, currency_str):
            if currency_str.lower() == "usd":
                return cls.USD
            elif currency_str.lower() == "tbt":
                return cls.TBT
            else:
                return cls.OTHER

    # probably should implement helper functions convert_to_usd
    # and convert_from_usd

    def get_value_in(self, currency):
        if self.currency == self.Currency.TBT:
            if currency == self.Currency.USD:
                return self.value / ExchangeRates.USD_TBT
        elif self.currency == self.Currency.USD:
            if currency == self.Currency.TBT:
                return self.value * ExchangeRates.USD_TBT
        
        return self.value

    value = models.DecimalField(max_digits=60, decimal_places=6, default=0)
    currency = models.IntegerField(
        choices = ((x.value, x.name.title()) for x in Currency)
    )


class Bid(models.Model):
    """
    When a potential shipper places a bid, it goes in this database.
    """

    def get_total(self, currency=Money.Currency.USD):
        """
        Computes the total sum in a very cool way.
        """
        return sum(
            [
                Money.objects.get(pk=self.__dict__[x]).get_value_in(currency)
                for x
                in self.__dict__.keys()
                if self.__dict__[x] and x in self.money_values
            ]
        )

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
    wages = models.ForeignKey(
        Money,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="wages",
    )
    retail_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="retail_price",
    )
    import_tax = models.ForeignKey(
        Money,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_tax",
    )
    dest_domestic_shipping = models.ForeignKey(
        Money,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="destination_domestic_shipping",
    )
    origin_domestic_shipping = models.ForeignKey(
        Money,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="origin_domestic_shipping",
    )
    international_shipping = models.ForeignKey(
        Money,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="international_shipping",
    )
    service_fee = models.ForeignKey(
        Money,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_fee",
    )
    origin_sales_tax = models.ForeignKey(
        Money,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="origin_sales_tax",
    )
    other_fees = models.ForeignKey(
        Money,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="other_fees",
    )

    # when you add a new field that should be added to the sum, add here with +"_id"
    money_values = [
        "wages_id",
        "retail_price_id",
        "import_tax_id",
        "dest_domestic_shipping_id",
        "origin_domestic_shipping_id",
        "international_shipping_id",
        "service_fee_id",
        "origin_sales_tax_id",
        "other_fees_id",
    ]


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
