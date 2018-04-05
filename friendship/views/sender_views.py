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
        wages = float(request.POST["wages"])
        order = Order.objects.get(pk=order_id)
        bid = Bid.objects.create(
            wages=wages,
            order=order,
            shipper_id=request.user.id,
        )

        # Just return another view after processing it.
        return open_orders(request, "recent")

@login_required
def user_open_bids(request):
    """
    This displays all the orders for the receiver.
    """
    qset = Bid.objects.filter(shipper=request.user)
    return render(request, 'friendship/user_open_bids.html', {
        'data': qset,
    })

@login_required
def sender_landing(request):
	return render(request, 'friendship/sender_landing.html', {
		'data': [request, ],
	})