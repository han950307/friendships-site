from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

from ..models import (
    Order,
    Bid,
    OrderAction,
)

import datetime


# Create your views here.

def get_min_bid(order):
    """
    Given an order, returns the min bid object.
    """
    bids = Bid.objects.filter(order=order)
    min_tups = [(x.bid_amount, x) for x in bids]
    if min_tups:
        min_bid = min(min_tups)
        min_bid = min_bid[1]
    else:
        min_bid = None
    return min_bid


def order_details(request, pk):
    """
    Given the order_id (pk), displays its info.
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        order = Order.objects.get(pk=pk)
        actions = OrderAction.objects.filter(order=pk)
        for action in actions:
            if not action.text:
                action.text = OrderAction.Action(action.action)
        return render(request, 'friendship/order_details.html', {
            'order': order,
            'actions': actions,
        })


def open_orders(request, filter):
    """
    View currently open orders.
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    elif not request.session["is_shipper"]:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    else:
        # Only display orders within a day ago.
        timelim = datetime.datetime.now() - datetime.timedelta(days=1)
        qset = Order.objects.filter(date_placed__gte=timelim)

        # Get minimum bid.
        for order in qset:
            min_bid = get_min_bid(order)
            if not min_bid:
                order.min_bid = "No current bids"
            else:
                order.min_bid = min_bid

        return render(request, 'friendship/open_orders.html', {
            'orders': qset
        })

