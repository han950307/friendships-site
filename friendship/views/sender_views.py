from ..models import UserInfo, Order, Bid

from .order_views import open_orders

from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

def make_bid(request, order_id):
    """
    Make bid view. Allows sender to make a bid for the order.
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        user_info = UserInfo.objects.get(pk=request.user.id)
        if not user_info.is_shipper:
            error(request, 'You do not have permissions to access this page.')
            return redirect('friendship:index')
        order = Order.objects.get(pk=order_id)
        return render(request, 'friendship/make_bid.html', {'order' : order})


def make_bid_process(request, order_id):
    """
    Processes make bid
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        user_info = UserInfo.objects.get(pk=request.user.id)
        # Must be a shipper.
        if not user_info.is_shipper:
            error(request, 'You do not have permissions to access this page.')
            return redirect('friendship:index')
        bid_amount = request.POST["bid_amount"]
        order = Order.objects.get(pk=order_id)
        Bid.objects.create(
            bid_amount=bid_amount,
            order=order,
            shipper_id=request.user.id,
        )

        # Just return another view after processing it.
        return open_orders(request, "recent")

