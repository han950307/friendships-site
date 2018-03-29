
from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

from friendship.models import (
    Order,
    ShippingAddress,
    OrderAction,
    Image
)

from friendship.forms import (
    UploadPictureForm
)

import datetime, pytz


def upload_picture_view(request, order_id):
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        orders = Order.objects.filter(pk=order_id)

        # if multiple orders or no order found with that id.
        if len(orders) != 1:
            error(request, 'Order not found')
            return redirect('friendship:receiver_landing')
        else:
            order = orders[0]
            return render(
                request,
                'friendship/upload_picture.html',
                {'order': order}
            )


def upload_picture_process(request, order_id):
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    elif request.method == "POST":
        form = UploadPictureForm(request.POST, request.FILES)
        order = Order.objects.get(pk=order_id)

        if form.is_valid():
            image = Image.objects.create(
                user=request.user,
                order=order,
                image=form.cleaned_data["picture"],
                mimetype="0",
                image_type="0"
            )
            OrderAction.objects.create(
                order=order,
                action=OrderAction.Action.BANKNOTE_UPLOADED
            )
            return redirect('friendship:order_details', pk=order_id)
        else:
            error(request, 'Bad image')
            return redirect('friendship:upload_picture_view', order_id=order_id)
    else:
        error(request, 'Must be a post request')
        return redirect('friendship:order_details', pk=order_id)


def receiver_landing_view(request):
    """
    This is a page for a form for making an order.
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:

        primary_address = ShippingAddress.objects.filter(
            user=request.user
        ).filter(
            primary=True
        )
        if primary_address:
            address = primary_address[0]
        else:
            address = None
        return render(request, 'friendship/receiver_landing.html', {'address': address})


def place_order_process(request):
    """
    When order is placed, it takes it to this page.
    """
    # render view for returning to dashboard or requesting another item
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        try:
            url = request.POST['url']
            merchandise_type = request.POST['merchandise_type']
            quantity = int(request.POST['quantity'])
            bid_time = int(request.POST['bid_time'])
            if (merchandise_type == "shoes"):
                thetype = Order.MerchandiseType.SHOES
            else:
                thetype = Order.MerchandiseType.OTHER
            desc = request.POST['desc']
        except (KeyError, ValueError):
            error(request, 'You didn\'t fill out something or you' + \
                ' didn\'t enter a value for quantity.')
            return render(request, 'friendship/place_order.html', {})
        else:
            # TODO should change this to receiver's choice
            primary_address = ShippingAddress.objects.filter(
                user=request.user
            ).filter(
                primary=True
            )

            # If primary address does not exist, make them add one.
            if not primary_address:
                try:
                    shipping_address = request.POST['shipping_address']
                    phone = int(request.POST['phone'])
                except KeyError:
                    error(request, 'You didn\'t fill out something')
                    return render(request, 'friendship/place_order.html', {})
                address = ShippingAddress.objects.create(
                    user=request.user,
                    address=shipping_address,
                    phone=phone,
                    address_type=ShippingAddress.AddressType.RECEIVER_ADDRESS,
                    primary=True,
                )
            else:
                address = primary_address[0]

            # Calculate end time
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            bid_end_datetime = now + datetime.timedelta(hours=bid_time)

            # Make Order
            order = Order.objects.create(
                url=url,
                merchandise_type=thetype,
                quantity=quantity,
                description=desc,
                receiver=request.user,
                receiver_address=address,
                bid_end_datetime=bid_end_datetime,
            )

            # Add order action
            action = OrderAction.objects.create(
                order=order,
                action=OrderAction.Action.ORDER_PLACED,
            )

            return render(request, 'friendship/place_order_landing.html', {'order': order})
