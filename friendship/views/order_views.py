from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

from django.contrib.auth.models import User

from ..models import Order, Bid, ShippingAddress, Message

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
        if order.receiver != request.user and order.shipper != request.user:
            error(request, 'You\'ve got the wrong user')
            return redirect('friendship:index')
        messages = Message.objects.filter(transaction=order)
        # authors = {}
        # if User.objects.get(order.shipper) is not None:
        #     authors[order.shipper] = User.objects.get(order.shipper).first_name
        # authors[order.receiver] = User.objects.get(order.receiver).first_name
        return render(request, 'friendship/order_details.html', {
            'order': order,
            'messages': messages,
            # 'shipper': authors,
        })

def all_open_orders(request, filter):
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

        return render(request, 'friendship/all_open_orders.html', {
            'orders': qset
        })


def user_open_orders(request):
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        qset = Order.objects.filter(receiver=request.user)
        return render(request, 'friendship/user_open_orders.html', {
            'orders': qset
        })

def match_bid(orderID, bidID):
    order = Order.objects.get(pk=orderID)
    bid = Bid.ojects.get(pk=bidID)
    order.shipper = bid.shipper
    order.shipper_address = ShippingAddress.objects.get(fk=bid.shipper).address
