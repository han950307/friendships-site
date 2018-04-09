"""
A file containing all cronjobs.
"""
from friendship.models import (
    Order,
    ShippingAddress,
    Bid,
    OrderAction
)
from friendship.views import match_with_shipper

import datetime
import pytz


def order_bid_update():
    """
    Checks for all open orders and sees if it should be matched with a shipper.
    """
    # first filter to see all objects with orders without a shipper that has
    # no more bidtime left.
    orders = Order.objects.filter(
        bid_end_datetime__lte=datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    ).filter(
        shipper=None
    )

    print("RUNNING!")

    # then just match.
    for order in orders:
        match_with_shipper(order)
