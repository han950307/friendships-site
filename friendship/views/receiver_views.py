from django.shortcuts import (
    render,
    redirect,
)

from backend.views import (
    create_order,
)

from friendship.models import (
    Order,
    ShippingAddress,
    OrderAction,
    Money,
)

from friendship.forms import (
    OrderForm,
    ShippingAddressForm,
    UploadPictureForm,
)
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.contrib import messages
from friendsite import settings
from friendship.views import(
    order_details,
    get_min_bid,
    match_with_shipper,
)
import datetime
import requests
import pytz
import omise
import base64


@login_required
def upload_picture_view(request, order_id):
    orders = Order.objects.filter(pk=order_id)

    # if multiple orders or no order found with that id.
    if len(orders) != 1:
        messages.error(request, 'Order not found')
        return redirect('friendship:receiver_landing')
    else:
        order = orders[0]
        return render(
            request,
            'friendship/upload_picture.html',
            {'order': order}
        )


@login_required
def upload_picture_process(request, order_id):
    if request.method == "POST":
        form = UploadPictureForm(request.POST, request.FILES)
        order = Order.objects.get(pk=order_id)

        if form.is_valid():
            imagef = form.cleaned_data["picture"]
            action = OrderAction.objects.create(
                order=order,
                action=OrderAction.Action.BANKNOTE_UPLOADED
            )
            order.latest_action = action
            order.save()
            return redirect('friendship:order_details', pk=order_id)
        else:
            messages.error(request, 'Bad image')
            return redirect('friendship:upload_picture_view', order_id=order_id)
    else:
        messages.debug(request, 'Must be a post request')
        return redirect('friendship:order_details', pk=order_id)


@login_required
def buy_now(request, order_id):
    order = Order.objects.get(pk=order_id)
    bids = Bid.objects.filter(order=order)
    if not bids:
        messages.error(request, 'There are no bids yet.')
        return redirect('friendship:order_details', order_id=order_id)
    match_with_shipper(order)


@login_required
def make_payment(request, order_id):
    return render(request, 'friendship/make_payment.html', {'order_id': order_id})


@login_required
def process_payment(request, order_id, currency):
    order = Order.objects.get(pk=order_id)
    total_amount = order.final_bid.get_total(currency)
    description = "Order-{}".format(order_id)
    if settings.DEBUG and settings.LOCAL:
        return_uri = "http://127.0.0.1:8000/"
    elif settings.DEBUG:
        return_uri = "https://dev.friendships.us/"
    else:
        return_uri = "https://www.friendships.us/"
    if order.receiver != request.user:
        print(order.receiver, request.user)
        return redirect('friendship:receiver_landing')
    omise_token = request.POST['omise_token']

    omise.api_secret = settings.OMISE_SECRET
    omise.api_public = settings.OMISE_PUBLIC

    charge = omise.Charge.create(
        amount=int(total_amount * 100),
        currency=str(Money.Currency(currency)).lower(),
        card=omise_token,
        description=description,
    )

    if charge.authorized == True and charge.paid == True:
        action = OrderAction.objects.create(
            order=order,
            action=OrderAction.Action.PAYMENT_RECEIVED,
        )
        order.latest_action = action
        order.save()
        messages.success(request, "Payment processed.")
        return redirect('friendship:order_details', order_id=order_id)

    # for now, just get the min
    form = ManualWireTransferForm()
    messages.error(request, "Payment failed. Please try again.")
    return order_details(request, order_id, {
        'manual_wire_transfer_form': form,
        'order_id': order_id,
    })


@login_required
def place_order(request):
    """
    This is a page for a form for making an order.
    """
    # CURRENTLY ONLY GET PRIMARY ADDRESS.
    if 'locale' not in request.session:
        request.session['locale'] = 'en-US'
    locale = request.session["locale"]
    user_addresses = request.user.shipping_addresses.filter(primary=True)

    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES, locale=locale)
        shipping_address_form = ShippingAddressForm(request.POST, locale=locale)
        if form.is_valid() and (shipping_address_form.is_valid() or len(user_addresses) > 0):
            # First create a shipping address if user has none
            if not user_addresses or shipping_address_form.is_valid():
                data_dict = {
                    'user': request.user,
                    'primary': True,
                    'address_type': ShippingAddress.AddressType.RECEIVER_ADDRESS,
                    **shipping_address_form.cleaned_data,
                }
                qset = ShippingAddress.objects.filter(user=request.user)
                shipping_address = ShippingAddress.objects.create(
                    **data_dict,
                )
                for user_address in user_addresses:
                    user_address.primary = False
                    user_address.save()
                print("CREATING SHIPPING ADDRESS")
            else:
                shipping_address = ShippingAddress.objects.get(pk=request.POST['shipping_address'])

            if "item_image" in form.cleaned_data:
                item_image = form.cleaned_data["item_image"]
            else:
                item_image = None

            bid_end_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) + \
                                datetime.timedelta(hours=int(form.cleaned_data['num_hours']))

            data_dict = {
                'url': form.cleaned_data['url'],
                'item_image': form.cleaned_data['item_image'],
                'merchandise_type': form.cleaned_data['merchandise_type'],
                'quantity': int(form.cleaned_data['quantity']),
                'size': form.cleaned_data['size'],
                'color': form.cleaned_data['color'],
                'description': form.cleaned_data['description'],
                'receiver': request.user,
                'receiver_address': shipping_address,
                'bid_end_datetime': bid_end_datetime,
                'estimated_weight': 0,
            }
            order = create_order(**{'data': data_dict})
            action = OrderAction.objects.create(
                order=order,
                action=OrderAction.Action.ORDER_PLACED,
            )
            order.latest_action = action
            order.save()

            return redirect('friendship:order_details', order_id=order.id)
        else:
            print(form.cleaned_data)
    else:
        form = OrderForm(request.GET, locale=locale)
        if not user_addresses:
            shipping_address_form = ShippingAddressForm(locale=locale)
        else:
            shipping_address_form = ShippingAddressForm(instance=user_addresses[0], locale=locale)
    return render(
        request,
        'friendship/place_order.html',
        {
            'form': form,
            'shipping_address_form': shipping_address_form,
            'user_addresses': user_addresses,
            'overlay': True,
        }
    )
