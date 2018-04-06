from django.contrib import messages
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
    PaymentAction,
    Message,
)

import datetime

from ..forms import (
    ManualWireTransferForm,
)
from django.core import serializers



def get_min_bid(order):
    """
    Given an order, returns the min bid object.
    """
    bids = Bid.objects.filter(order=order)
    bid_list = [(x.get_total(), x) for x in bids]
    if bids:
        return min(bid_list)[1]
    else:
        return None


@login_required
def order_details(request, order_id, **kwargs):
    """
    Given the order_id (pk), displays its info.
    """
    order = Order.objects.get(pk=order_id)
    if order.receiver != request.user and order.shipper != request.user:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('friendship:index')

    actions = OrderAction.objects.filter(order=order)

    data_dict = {}
    data_dict.update({
        'order': order,
        'actions': reversed(actions),
        'latest_action': order.latest_action,
        'min_bid': get_min_bid(order),
        'manual_wire_transfer_form': ManualWireTransferForm(),
    })
    data_dict.update(kwargs)

    data_dict.update({ k : v.value
                        for (k,v)
                        in OrderAction.Action._member_map_.items()
    })

    return render(request, 'friendship/order_details.html', data_dict)


@login_required
def confirm_order_price(request, order_id, choice):
    order = Order.objects.get(pk=order_id)
    if order.receiver != request.user and order.shipper != request.user:
        messages.error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')
    if choice == "True":
        action = OrderAction.objects.create(
            order=order,
            action=OrderAction.Action.PRICE_ACCEPTED,
            #action=OrderAction.Action.PAYMENT_RECEIVED,
        )
        order.latest_action = action
        order.save()
        form = ManualWireTransferForm()
        return order_details(request, order_id, **{'manual_wire_transfer_form': form})
    else:
        action = OrderAction.objects.create(
            order=order,
            action=OrderAction.Action.ORDER_DECLINED,
        )
        order.latest_action = action
        order.save()
        return redirect('friendship:order_details', order_id=order_id)


@login_required
def submit_wire_transfer(request, order_id):
    order = Order.objects.get(pk=order_id)
    if order.receiver != request.user and order.shipper != request.user:
        messages.error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')
    if request.method == 'POST':
        form = ManualWireTransferForm(request.POST, request.FILES)
        if form.is_valid():
            order.banknote_image = form.cleaned_data["banknote_image"]
            PaymentAction.objects.create(
                order=order,
                payment_type=PaymentAction.PaymentType.MANUAL_WIRE_TRANSFER,
                account_number = form.cleaned_data["account_number"]
            )
            action = OrderAction.objects.create(
                order=order,
                action=OrderAction.Action.BANKNOTE_UPLOADED,
                # action=OrderAction.Action.PAYMENT_RECEIVED,
            )
            order.latest_action = action
            order.save()
            return order_details(request, order_id)
    else:
        form = ManualWireTransferForm()

    return order_details(request, order_id, **{'manual_wire_transfer_form': form})

@login_required
def open_orders(request, filter):
    """
    View currently open orders.
    """
    if not request.session["is_shipper"]:
        messages.error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    else:
        # Only display orders within a day ago.
        timelim = datetime.datetime.now() - datetime.timedelta(days=1)
        qset = Order.objects.filter(date_placed__gte=timelim)

        # Get minimum bid.
        for order in qset:
            min_bid = get_min_bid(order)
            print(order, min_bid)
            if not min_bid:
                order.min_bid = "No current bids"
            else:
                order.min_bid = min_bid

        return render(request, 'friendship/all_open_orders.html', {
            'orders': qset
        })


@login_required
def user_open_orders(request):
    """
    This displays all the orders for the receiver.
    """
    qset = Order.objects.filter(receiver=request.user).union(Order.objects.filter(shipper=request.user))
    for order in qset:
        min_bid = get_min_bid(order)
        if not min_bid:
            order.min_bid = "No current bids"
        else:
            order.min_bid = min_bid
    return render(request, 'friendship/user_open_orders.html', {
        'orders': qset
    })
