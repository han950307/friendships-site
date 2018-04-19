"""
A file containing all cronjobs.
"""
from friendship.models import (
    Order,
    ShippingAddress,
    Bid,
    OrderAction
)
from friendship.views import match_with_shipper, create_action_for_order

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
    ).filter(
        latest_action__action__gt=OrderAction.Action.MATCH_NOT_FOUND
    )

    # then just match.
    for order in orders:
        match_with_shipper(order)


def order_bid_clean():
    """
    This function declines all the unfulfilled items (unpaid).
    """
    end_time = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(days=1)
    orders = Order.objects.filter(
        bid_end_datetime__lte=end_time
    ).filter(
        latest_action__action__lt=OrderAction.Action.BANKNOTE_UPLOADED
    ).filter(
        latest_action__action__gt=OrderAction.Action.MATCH_NOT_FOUND
    )

    for order in orders:
        create_action_for_order(order, OrderAction.Action.ORDER_DECLINED)
