"""
A file containing all cronjobs.
"""
from friendship.models import (
    Order,
    ShippingAddress,
    Bid,
    OrderAction
)
from friendship.views.order_views import get_min_bid

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


def match_with_shipper(order):
	"""
	Pick the lowest bidder and update the database.
	"""
	min_bid = get_min_bid(order)
	if not min_bid:
		# pair with one of friendship accounts.
		pass
	else:
		order.shipper = min_bid.shipper
		# make shipper choose a shipping address when they're matched.
		order.save()

	print(min_bid.__dict__)
	order.final_bid = min_bid
	action = OrderAction.objects.create(
		order=order,
		action=OrderAction.Action.MATCH_FOUND
	)
	order.latest_action = action
	order.save()
