from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)
from django.contrib.auth.decorators import login_required
from ..models import (
    Order,
    Bid,
    OrderAction,
    ShippingAddress,
    Message,
)

import datetime


# Create your views here.

def get_min_bid(order):
    """
    Given an order, returns the min bid object.
    """
    bids = Bid.objects.filter(order=order)
    if bids:
        return min(bids)
    else:
        return None


@login_required
def order_details(request, pk):
    """
    Given the order_id (pk), displays its info.
    """
    order = Order.objects.get(pk=pk)
    if order.receiver != request.user and order.shipper != request.user:
        error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')
    messages = Message.objects.filter(transaction=order)
    first = 0
    if len(messages) != 0:
        first = messages.first().pk

    actions = OrderAction.objects.filter(order=pk)
    for action in actions:
        if not action.text:
            action.text = OrderAction.Action(action.action)

    return render(request, 'friendship/order_details.html', {
        'order': order,
        'messages': messages,
        'first': first,
        'actions': actions,
    })


@login_required
def open_orders(request, filter):
    """
    View currently open orders.
    """
    if not request.session["is_shipper"]:
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

        return render(request, 'friendship/all_open_orders.html', {
            'orders': qset
        })


@login_required
def user_open_orders(request):
    qset = Order.objects.filter(receiver=request.user).union(Order.objects.filter(shipper=request.user))
    return render(request, 'friendship/user_open_orders.html', {
        'orders': qset
    })


def match_bid(order_id, bid_id):
    order = Order.objects.get(pk=order_id)
    bid = Bid.ojects.get(pk=bid_id)
    order.shipper = bid.shipper
    # TODO: should default to primary shipping address but able to confirm.
    order.shipper_address = ShippingAddress.objects.get(fk=bid.shipper)[0]
