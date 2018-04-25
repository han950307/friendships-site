"""
A file containing all cronjobs.
"""
from backend.views import (
    get_cur_wage,
    make_bid_backend,
)
from friendship.models import (
    Order,
    ShippingAddress,
    Money,
    Bid,
    OrderAction
)
from friendship.views import (
    match_with_shipper,
    create_action_for_order
)
from friendsite import settings

import datetime
import pytz
import random


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


def order_bid_trickle():
    """
    Run this to simulate people bidding (bid trickle algorithm)
    """
    open_orders = Order.objects.filter(
        bid_end_datetime__gt=datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    ).filter(
        shipper=None
    ).filter(
        latest_action__action__lte=OrderAction.Action.MATCH_FOUND
    )

    for order in open_orders:
        trickle_down_to_bid = Bid.objects.filter(order=order).filter(bid_trickle=True)
        
        # If we don't have a trickle down bid registered, then continue.
        if not trickle_down_to_bid:
            continue
        else:
            trickle_down_to_bid = trickle_down_to_bid[0]

        # Skip with a probability p
        if random.random() > settings.BID_TRICKLE_ACCEPT_PROBABILITY:
            continue

        # Construct data dict for bid object
        data_dict = {
            'bid_trickle': False,
            'currency': Money.Currency.USD,
            'wages': get_cur_wage(order),
            'retail_price': trickle_down_to_bid.retail_price.get_value(),
        }

        make_bid_backend(trickle_down_to_bid.shipper, order, **data_dict)
