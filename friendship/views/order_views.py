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
    ShipperInfo,
    TrackingNumber,
    Money,
)

import datetime
import pytz
import braintree
import math
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
    bids = Bid.objects.filter(order=order).filter(bid_trickle=False)
    if bids:
        return min(bids)
    else:
        return None


def create_action_for_order(order, action_enum):
    action = OrderAction.objects.create(
        order=order,
        action=action_enum
    )
    order.latest_action = action

    order.save()


def match_with_shipper(order):
    """
    Pick the lowest bidder and update the database.
    """
    min_bid = get_min_bid(order)
    if not min_bid:
        if order.bid_end_datetime < datetime.datetime.utcnow().replace(tzinfo=pytz.utc):
            create_action_for_order(order, OrderAction.Action.MATCH_NOT_FOUND)
        return

    else:
        order.shipper = min_bid.shipper
        # make shipper choose a shipping address when they're matched.
        create_action_for_order(order, OrderAction.Action.MATCH_FOUND)
        order.final_bid = min_bid
        order.save()

    body = "Dear {first_name},\n\nWe have found a match for you" + \
            "! Please visit {url} for details and pay " + \
            "within 24 hours to receive your item.\n\n" + \
            "Your final price is {total_price_usd} ({total_price_thb}).\n"

    body_str = body.format(
        first_name=order.receiver.first_name,
        url="https://www.friendships.us/order_details/{}".format(order.id),
        total_price_usd=order.final_bid.get_total_str(),
        total_price_thb=order.final_bid.get_total_str(Money.Currency.THB),
    )

    if not settings.LOCAL:
        mail.send_mail(
            "Your Order #{} Match Found!".format(order.id),
            body_str,
            "FriendShips <no-reply@friendships.us>",
            [order.receiver.email],
        )


@login_required
def order_details(request, order_id, **kwargs):
    """
    Given the order_id (pk), displays its info.
    """
    order = Order.objects.get(pk=order_id)
    if order.receiver != request.user and request.user.shipper_info.shipper_type != ShipperInfo.ShipperType.FRIENDSHIP_BIDDER:
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

    us_tracking = TrackingNumber.objects.filter(
        order=order
    ).filter(
        shipping_stage=TrackingNumber.ShippingStage.MERCHANT_TO_SHIPPER
    )
    thai_tracking = TrackingNumber.objects.filter(
        order=order
    ).filter(
        shipping_stage=TrackingNumber.ShippingStage.DOMESTIC_TO_RECEIVER
    )

    data_dict.update({
        'us_tracking': us_tracking[0] if us_tracking else None,
        'thai_tracking': thai_tracking[0] if thai_tracking else None
    })

    if min_bid:
        thb_total = math.ceil(min_bid.get_total(currency=Money.Currency.THB))
    else:
        thb_total = "0"

    data_dict.update({
        'order': order,
        'order_url': order_url,
        'actions': reversed(actions),
        'latest_action': order.latest_action,
        'min_bid': min_bid,
        'subtotal': Money.format_value(subtotal, currency),
        'usd': Money.Currency.USD,
        'thb': Money.Currency.THB,
        'usd_str': str(Money.Currency.USD).upper(),
        'thb_str': str(Money.Currency.THB).upper(),
        'thb_total': str(thb_total),
        'currency': currency,
        'manual_wire_transfer_form': ManualWireTransferForm(),
    })
    data_dict.update(kwargs)

    data_dict.update({ k : v.value
                        for (k,v)
                        in OrderAction.Action._member_map_.items()
    })

    # Braintree Setup
    if settings.DEBUG:
        env = "sandbox"
    else:
        env = "production"

    gateway = braintree.BraintreeGateway(access_token=settings.BRAINTREE_ACCESS_TOKEN)
    client_token = gateway.client_token.generate()
    client = "{" + \
        f"{env}: '{client_token}'" + \
    "}"
    data_dict["braintree_client"] = client
    data_dict["payment_env"] = env

    return render(request, 'friendship/order_details.html', data_dict)


@login_required
def process_braintree_payment(request):
    # get data
    order_id = request.POST["order_id"]
    braintree_nonce = request.POST.get("braintree_nonce", False)

    # get order
    order = Order.objects.filter(pk=order_id).filter(receiver=request.user)
    if not order:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('friendship:index')
    else:
        order = order[0]

    # Check if the paid amount is same as the order's total amount.
    paid_amount = int(braintree_nonce)
    order_amount = int(math.ceil(order.final_bid.get_total(currency=Money.Currency.THB)))

    if paid_amount != order_amount:
        messages.error(request, 'The amount paid does not match the total amount of the order.')
        return redirect('friendship:order_details', order_id=order_id)


    # initialize gateway
    # gateway = braintree.BraintreeGateway(access_token=settings.BRAINTREE_ACCESS_TOKEN)
    # currency = Money.Currency.THB
    # value = math.ceil(order.final_bid.get_total(currency))

    # result = gateway.transaction.sale({
    #     "amount": str(value),
    #     "merchant_account_id": str(currency).upper(),
    #     "payment_method_nonce" : braintree_nonce,
    #     "order_id" : "friendshipsorder{}".format(order.id),
    #     "descriptor": {
    #       "name": "FriendShips *ecommerce"
    #     },
    # })
    # if result.is_success:
    create_action_for_order(order, OrderAction.Action.PAYMENT_RECEIVED)
    PaymentAction.objects.create(
        order=order,
        payment_type=PaymentAction.PaymentType.PAYPAL,
    )
    messages.success(request, "Payment processed.")

    return redirect('friendship:order_details', order_id=order_id)


@login_required
def end_bid(request, order_id, **kwargs):
    """
    When the receiver clicks buy now button during the bid period, this logic gets
    executed.
    """
    order = Order.objects.get(pk=order_id)

    # Check if the request's user actually placed the order.
    if order.receiver != request.user:
        messages.error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')

    # Replace the bid end datetime with current time because it ended now.
    order.bid_end_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    order.save()

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
    # When order price is confirmed
    if choice == "True":
        create_action_for_order(order, OrderAction.Action.PRICE_ACCEPTED)
        form = ManualWireTransferForm()
        return order_details(request, order_id, **{'manual_wire_transfer_form': form})
    # When order is declined
    else:
        create_action_for_order(order, OrderAction.Action.ORDER_DECLINED)
        return redirect('friendship:order_details', order_id=order_id)


@login_required
def submit_wire_transfer(request, order_id):
    """
    Wire transfer logic
    """
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
            )
            create_action_for_order(order, OrderAction.Action.BANKNOTE_UPLOADED)
            order.save()
            return redirect('friendship:order_details', order_id=order_id)
    else:
        form = ManualWireTransferForm()

    return order_details(request, order_id, **{'manual_wire_transfer_form': form})


@login_required
def open_orders(request, filter):
    """
    View currently open orders for the senders.
    """
    if not request.session["is_shipper"]:
        messages.error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    else:
        # Only display orders that are due later than right now.
        right_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        qset = Order.objects.filter(
            bid_end_datetime__gte=right_now
        ).order_by(
            '-bid_end_datetime'
        ).filter(
            shipper=None
        ).filter(
            latest_action__action__lte=OrderAction.Action.MATCH_FOUND
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
    qset = Order.objects.filter(
        receiver=request.user
    ).order_by(
        '-date_placed'
    )
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
