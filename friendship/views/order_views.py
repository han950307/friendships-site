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
    Money,
)

import datetime
import pytz
from django.core import mail
from friendsite import settings

from ..forms import (
    ManualWireTransferForm,
)
from django.core import serializers


def get_min_bid(order):
    """
    Given an order, returns the min bid object.
    """
    bids = Bid.objects.filter(order=order)
    if bids:
        return min(bids)
    else:
        return None


def match_with_shipper(order):
    """
    Pick the lowest bidder and update the database.
    """
    min_bid = get_min_bid(order)
    if not min_bid:
        if order.bid_end_datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.utc):
            action = OrderAction.objects.create(
                order=order,
                action=OrderAction.Action.MATCH_NOT_FOUND
            )
        return

    else:
        order.shipper = min_bid.shipper
        # make shipper choose a shipping address when they're matched.
        action = OrderAction.objects.create(
            order=order,
            action=OrderAction.Action.MATCH_FOUND,
        )
        order.final_bid = min_bid
        order.save()

    body = "Dear {first_name},\n\nWe have found a match for you with {shipper_name}" + \
            "! Please visit {url}, confirm the final price, and send in the payment" + \
            "within 24 hours to receive your item.\n\n" + \
            "Your final price is {total_price_usd} ({total_price_thb}).\n"

    if order.shipper.shipper_info.name:
        shipper_name = order.shipper.shipper_info.name
    else:
        shipper_name = order.shipper.first_name

    body_str = body.format(
        first_name=order.receiver.first_name,
        shipper_name=shipper_name,
        url="https://www.friendships.us/order_details/{}".format(order.id),
        total_price_usd=order.final_bid.get_total_str(),
        total_price_thb=order.final_bid.get_total_str(Money.Currency.THB),
    )

    mail.send_mail(
        "Your Order #{} Match Found!".format(order.id),
        body_str,
        "no-reply@friendships.us",
        [order.receiver.email],
    )

    order.latest_action = action
    order.save()


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

    # default currency to USD
    if "currency" not in request.session:
        request.session["currency"] = Money.Currency.USD

    # calculate subtotal
    currency = request.session["currency"]

    subtotal = 0
    min_bid = get_min_bid(order)
    
    if min_bid:
        if min_bid.retail_price:
            subtotal += min_bid.retail_price.get_value(currency)
        if min_bid.service_fee:
            subtotal += min_bid.service_fee.get_value(currency)

    data_dict = {}
    if len(order.url) > 50:
        order_url = order.url[0:47] + "..."
    else:
        order_url = order.url

    data_dict.update({
        'order': order,
        'order_url': order_url,
        'actions': reversed(actions),
        'latest_action': order.latest_action,
        'min_bid': min_bid,
        'subtotal': Money.format_value(subtotal, currency),
        'usd': Money.Currency.USD,
        'thb': Money.Currency.THB,
        'currency': currency,
        'manual_wire_transfer_form': ManualWireTransferForm(),
    })
    data_dict.update(kwargs)

    data_dict.update({ k : v.value
                        for (k,v)
                        in OrderAction.Action._member_map_.items()
    })

    return render(request, 'friendship/order_details.html', data_dict)


@login_required
def end_bid(request, order_id, **kwargs):
    order = Order.objects.get(pk=order_id)

    # If the order is not the receiver, then don't do it.
    if order.receiver != request.user:
        messages.error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')

    # match with lowest shipper and end it.
    match_with_shipper(order)

    # reload the page.
    return redirect('friendship:order_details', order_id=order_id)


@login_required
def confirm_order_price(request, order_id, choice):
    order = Order.objects.get(pk=order_id)
    if order.receiver != request.user and order.shipper != request.user:
        messages.error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')
    if order.latest_action == OrderAction.Action.ORDER_DECLINED:
        messages.error(request, 'Sorry, but you already declined this order.')
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
            return redirect('friendship:order_details', order_id=order_id)
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
        # Only display orders that are due later than right now.
        right_now = datetime.datetime.now()
        qset = Order.objects.filter(
            bid_end_datetime__gte=right_now
        ).order_by(
            '-bid_end_datetime'
        ).filter(
            shipper=None
        )

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

    data_dict = {}
    data_dict.update({ k : v.value
                        for (k,v)
                        in OrderAction.Action._member_map_.items()
    })
    data_dict['orders'] = qset

    return render(request, 'friendship/user_open_orders.html', data_dict)
