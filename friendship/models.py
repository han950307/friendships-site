from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class ShipperList(models.Model):
    """
    Contains a list of shippers.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class ShippingAddress(models.Model):
    """
    Keeps track of shipping addresses for each user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    address = models.CharField(max_length=1000)
    
    # Each shipping address should have an associated phone number.
    phone = models.CharField(max_length=50, null=True)

    # Will be referencing an enum for sender_address, receiver_address.
    address_type = models.IntegerField()

    primary = models.BooleanField()


class Order(models.Model):
    """
    An entry gets created when a receiver places an order.
    """
    url = models.URLField()
    merchandise_type = models.IntegerField()
    # When the receiver places a request
    date_placed = models.DateTimeField(auto_now_add=True)
    # When it was delivered
    date_completed = models.DateTimeField(null=True)
    status = models.IntegerField()
    description = models.TextField()
    quantity = models.IntegerField()
    shipper = models.ForeignKey(
        User,
        related_name="shipper",
        on_delete=models.SET_NULL,
        null=True
    )
    shipper_address = models.ForeignKey(
        ShippingAddress,
        related_name="shipper_address",
        on_delete=models.SET_NULL,
        null=True
    )
    receiver = models.ForeignKey(
        User,
        related_name="receiver",
        on_delete=models.CASCADE,
    )
    receiver_address = models.ForeignKey(
        ShippingAddress,
        related_name="receiver_address",
        on_delete=models.CASCADE,
    )


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
    )
    bid_amount = models.DecimalField(max_digits=50, decimal_places=4)
    currency = models.CharField(max_length=15)


class Image(models.Model):
    date_uploaded = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
    )
    image = models.ImageField()
    mimetype = models.CharField(max_length=25)
    # Bank-slip or whatever
    image_type = models.IntegerField()


class Message(models.Model):
    date_sent = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
    )
    content = models.CharField(max_length=5000)
