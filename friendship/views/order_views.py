from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

from ..models import Order, Bid

import datetime


# Create your views here.

def get_min_bid(order):
    """
    Given an order, returns the min bid.
    """
    bids = Bid.objects.filter(order=order)
    min_arr = [x.bid_amount for x in bids]
    if min_arr:
        min_bid = min(min_arr)
    else:
        min_bid = "No current bids"
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
        return render(request, 'friendship/order_details.html', {
            'order': order
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
            order.min_bid = get_min_bid(order)

        return render(request, 'friendship/open_orders.html', {
            'orders': qset
        })

