from django import template
from friendship.models import Money, Bid

import math
from babel import dates

register = template.Library()


@register.simple_tag
def get_bid_total_str(bid, currency):
    if not bid:
        return None
    return bid.get_total_str(currency)


@register.simple_tag
def get_money_str(money, currency):
    if not money:
        return None
    return money.get_value_str(currency)


@register.simple_tag
def get_lowest_bid_str(order, currency):
	bids = Bid.objects.filter(order=order)
	lowest_bid = None
	lowest_val = None
	for bid in bids:
		val = bid.get_total()
		if not lowest_val or val < lowest_val:
			lowest_bid = bid
			lowest_val = val

	if lowest_bid:
		return lowest_bid.get_total_str(currency)
	return None


@register.simple_tag
def get_date_str(datetime, str_format="datetime", locale="en_US"):
	"""
	returns a formatted datetime given a datetime object.
	"""
	if str_format == "date":
		return dates.format_date(datetime, locale=locale)
	elif str_format == "time":
		return dates.format_time(datetime, locale=locale)
	else:
		return dates.format_datetime(datetime, locale=locale)
