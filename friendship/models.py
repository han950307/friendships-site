from django.db import models
from django.conf import settings


# Create your models here.
class UserInfo(models.Model):
    """
    Links to the User model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    shipping_address = models.CharField(max_length=500)
    phone = models.CharField(max_length=25)
    is_receiver = models.BooleanField(default=True)
    is_sender = models.BooleanField(default=False)


class Order(models.Model):
    """
    An entry gets created when a receiver places an order.
    """
    url = models.URLField()
    merchandise_type = models.IntegerField()
    # When the receiver places a request
    date_placed = models.DateTimeField(auto_now_add=True)
    # When the sender accepts the request
    date_accepted = models.DateTimeField(null=True)
    # When the receiver agrees to the weight and size & money
    date_verified = models.DateTimeField(null=True)
    # When it was delivered
    date_completed = models.DateTimeField(null=True)
    status = models.IntegerField()
    sender_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sender_id",
        on_delete=models.CASCADE,
    )
    receiver_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="receiver_id",
        on_delete=models.CASCADE,
    )


class Image(models.Model):
    date_uploaded = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    order_id = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
    )
    image = models.ImageField()
    mimetype = models.CharField(max_length=25)
    # Bank-slip or whatever
    image_type = models.IntegerField()
