from django import template
from friendship.models import Money

import math

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
