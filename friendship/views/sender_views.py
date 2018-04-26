from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin

from formtools.wizard.views import SessionWizardView

from friendship.models import Order, Bid, ShipperInfo, Money, OrderAction, TrackingNumber
from friendship.views import (
    open_orders,
    create_action_for_order,
)
from friendship.forms import (
    SenderRegistrationForm,
    TravelerRegistrationForm,
    ShippingCompanyRegistrationForm,
    BidForm,
    UploadItemPurchasedReceiptForm,
    UploadTrackingNumberForm,
    ConfirmBanknoteForm,
    FlightAttendantRegistrationForm,

)
from backend.views import (
    create_money_object,
    make_bid_backend,
)
from friendsite import settings

import os
import decimal
import math


@login_required
def make_bid(request, order_id):
    """
    Make bid view. Allows sender to make a bid for the order.
    """
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')

    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            data_dict = {x: v for x, v in form.cleaned_data.items()}
            data_dict["currency"] = int(data_dict["currency"])
            data_dict["service_fee"] = decimal.Decimal(data_dict["retail_price"]) * settings.SERVICE_FEE_RATE
            make_bid_backend(request.user, order, **data_dict)
            return redirect('friendship:open_orders', "all")
    else:
        form = BidForm()

    return render(request, 'friendship/make_bid.html', {'order' : order, 'form': form})


class SenderRegistrationWizard(LoginRequiredMixin, SessionWizardView):
    template_name = 'friendship/sender_registration.html'
    form_list = [SenderRegistrationForm]
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'id_images'))

    def done(self, form_list, form_dict, **kwargs):
        user = self.request.user
        shipper_type = int(form_dict['0'].cleaned_data["shipper_type"])
        phone_number = form_dict['1'].cleaned_data["phone_number"]
        shipper_info = ShipperInfo.objects.create(
            user=user,
            shipper_type=shipper_type,
            verified=False,
            phone_number=phone_number,
        )
        if (shipper_type == ShipperInfo.ShipperType.TRAVELER):
            id_image = form_dict['1'].cleaned_data["id_image"]
            shipper_info.id_image = id_image
            shipper_info.name = user.first_name + " " + user.last_name
        elif shipper_type == ShipperInfo.ShipperType.FLIGHT_ATTENDANT:
            pass
        elif shipper_type == ShipperInfo.ShipperType.SHIPPING_COMPANY:
            name = form_dict['1'].cleaned_data["name"]
            shipper_info.name = name
        shipper_info.save()

        return redirect('friendship:index')

    def process_step(self, form):
        if "shipper_type" in form.cleaned_data:
            shipper_type = int(form.cleaned_data["shipper_type"])
            if shipper_type == ShipperInfo.ShipperType.TRAVELER:
                self.form_list.update({'1': TravelerRegistrationForm})
            elif shipper_type == ShipperInfo.ShipperType.FLIGHT_ATTENDANT:
                self.form_list.update({'1': FlightAttendantRegistrationForm})
            elif shipper_type == ShipperInfo.ShipperType.SHIPPING_COMPANY:
                self.form_list.update({'1': ShippingCompanyRegistrationForm})
            else:
                pass
        return super(SenderRegistrationWizard, self).process_step(form)


def get_lowest_user_bid(order, user):
    bids = Bid.objects.filter(order=order).filter(shipper=user).filter(bid_trickle=False)
    lowest_val = None
    lowest_bid = None
    for bid in bids:
        val = bid.get_total()
        if not lowest_val or val < lowest_val:
            lowest_bid = bid
            lowest_val = val

    return lowest_bid


@login_required
def user_open_bids(request):
    """
    This displays all the orders for the receiver.
    """
    # Initialize data dict with all the order actions
    data_dict = {}
    data_dict.update({ k : v.value
                        for (k,v)
                        in OrderAction.Action._member_map_.items()
    })

    # populate with current active orders
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    qset = Bid.objects.filter(
        shipper=request.user
    ).filter(
        bid_trickle=False
    ).filter(
        order__latest_action__action__lt=OrderAction.Action.MATCH_FOUND
    ).order_by(
        'order', '-order__bid_end_datetime'
    ).distinct(
        'order'
    )

    data_dict['active_orders'] = [
        get_lowest_user_bid(x.order, request.user)
        for x
        in qset
    ]

    # populate it with matched orders.
    qset = Order.objects.filter(
        shipper=request.user
    ).filter(
        latest_action__action__gte=OrderAction.Action.MATCH_FOUND
    ).filter(
        latest_action__action__lt=OrderAction.Action.ORDER_FULFILLED
    ).filter(
        final_bid__shipper=request.user
    ).order_by(
        '-bid_end_datetime'
    )

    data_dict['matched_orders'] = [
        x.final_bid
        for x
        in qset
    ]
    return render(request, 'friendship/user_open_bids.html', data_dict)


@login_required
def confirm_banknote(request, order_id):
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    order = Order.objects.filter(id=order_id).filter(shipper=request.user)
    if not order:
        error(request, 'no orders found')
        return redirect('friendship:index')
    order = order[0]

    if request.method == 'POST':
        form = ConfirmBanknoteForm(request.POST)
        if form.is_valid():
            data_dict = {x: v for x, v in form.cleaned_data.items()}
            if data_dict["is_ok"] == "True":
                create_action_for_order(order, OrderAction.Action.PAYMENT_RECEIVED)
            else:
                create_action_for_order(order, OrderAction.Action.ORDER_DECLINED)
            return redirect('friendship:user_open_bids')
    else:
        thb_total = math.ceil(order.final_bid.get_total(currency=Money.Currency.THB))
        new_val = "\u0E3F{}".format(math.ceil(thb_total - thb_total * settings.MANUAL_BANK_TRANSFER_DISCOUNT))
        form = ConfirmBanknoteForm()

    return render(request, 'friendship/confirm_banknote.html', {'order' : order, 'form': form, 'val': new_val})


@login_required
def confirm_item_purchased_receipt(request, order_id):
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    order = Order.objects.filter(id=order_id).filter(shipper=request.user)
    if not order:
        error(request, 'no orders found')
        return redirect('friendship:index')
    order = order[0]

    if request.method == 'POST':
        form = UploadItemPurchasedReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            data_dict = {x: v for x, v in form.cleaned_data.items()}
            order.item_receipt_image = data_dict["picture"]
            order.save()
            create_action_for_order(order, OrderAction.Action.ITEM_ORDERED_BY_FRIENDSHIPS)
            return redirect('friendship:user_open_bids')
    else:
        form = UploadItemPurchasedReceiptForm()

    return render(request, 'friendship/confirm_item_purchased_receipt.html', {'order' : order, 'form': form})


@login_required
def confirm_item_shipped_by_merchant(request, order_id):
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    order = Order.objects.filter(id=order_id).filter(shipper=request.user)
    if not order:
        error(request, 'no orders found')
        return redirect('friendship:index')
    order = order[0]

    if request.method == 'POST':
        form = UploadTrackingNumberForm(request.POST, request.FILES)
        if form.is_valid():
            data_dict = {x: v for x, v in form.cleaned_data.items()}
            TrackingNumber.objects.create(
                order=order,
                provider=data_dict["provider"],
                tracking_number=data_dict["tracking_number"],
                shipping_stage=TrackingNumber.ShippingStage.MERCHANT_TO_SHIPPER,
            )
            create_action_for_order(order, OrderAction.Action.ITEM_SHIPPED_BY_MERCHANT)
            return redirect('friendship:user_open_bids')
    else:
        form = UploadTrackingNumberForm()

    return render(request, 'friendship/confirm_item_shipped_by_merchant.html', {'order' : order, 'form': form})


@login_required
def confirm_item_shipped_in_thailand(request, order_id):
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    order = Order.objects.filter(id=order_id).filter(shipper=request.user)
    if not order:
        error(request, 'no orders found')
        return redirect('friendship:index')
    order = order[0]

    if request.method == 'POST':
        form = UploadTrackingNumberForm(request.POST, request.FILES)
        if form.is_valid():
            data_dict = {x: v for x, v in form.cleaned_data.items()}
            TrackingNumber.objects.create(
                order=order,
                provider=data_dict["provider"],
                tracking_number=data_dict["tracking_number"],
                shipping_stage=TrackingNumber.ShippingStage.DOMESTIC_TO_RECEIVER,
            )
            create_action_for_order(order, OrderAction.Action.ITEM_SHIPPED_DOMESTICALLY_BY_SHIPPER)
            return redirect('friendship:user_open_bids')
    else:
        form = UploadTrackingNumberForm()

    return render(request, 'friendship/confirm_item_shipped_in_thailand.html', {'order' : order, 'form': form})


@login_required
def confirm_item_received(request, order_id):
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    order = Order.objects.filter(id=order_id).filter(shipper=request.user)
    if not order:
        error(request, 'no orders found')
        return redirect('friendship:index')
    order = order[0]
    create_action_for_order(order, OrderAction.Action.ITEM_RECEIVED_BY_SHIPPER)
    return redirect('friendship:user_open_bids')


@login_required
def confirm_item_arrived_in_thailand(request, order_id):
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    order = Order.objects.filter(id=order_id).filter(shipper=request.user)
    if not order:
        error(request, 'no orders found')
        return redirect('friendship:index')
    order = order[0]
    create_action_for_order(order, OrderAction.Action.ITEM_ARRIVED_IN_THAILAND)
    return redirect('friendship:user_open_bids')


@login_required
def sender_landing(request):
    if request.session["is_shipper"] != True:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    return redirect('friendship:user_open_bids')
    return render(request, 'friendship/sender_landing.html', {
        'data': [request, ],
    })
