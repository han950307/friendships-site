from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

from friendship.models import Order, Bid
from friendship.views import open_orders


@login_required
def make_bid(request, order_id):
    """
    Make bid view. Allows sender to make a bid for the order.
    """
    if not request.session["is_shipper"]:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    else:
        order = Order.objects.get(pk=order_id)
        return render(request, 'friendship/make_bid.html', {'order' : order})


@login_required
def make_bid_process(request, order_id):
    """
    Processes make bid
    """
    if not request.session["is_shipper"]:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    else:
        bid_amount = request.POST["bid_amount"]
        order = Order.objects.get(pk=order_id)
        Bid.objects.create(
            bid_amount=bid_amount,
            order=order,
            shipper_id=request.user.id,
        )

        # Just return another view after processing it.
        return open_orders(request, "recent")

