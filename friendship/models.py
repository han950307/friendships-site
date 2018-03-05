from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# Create your models here.
class UserInfo(models.Model):
    """
    Links to the User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    shipping_address = models.CharField(max_length=500)
    phone = models.CharField(max_length=25)
    is_receiver = models.BooleanField(default=True)
    is_shipper = models.BooleanField(default=False)


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
    shipper = models.ForeignKey(
        User,
        related_name="shipper",
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        User,
        related_name="receiver",
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
