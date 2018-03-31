
from django.contrib.messages import error

from django.shortcuts import (
    render,
    redirect,
)

from friendship.models import (
    Order,
    ShippingAddress,
    OrderAction,
    Image,
)

from friendship.forms import (
    UploadPictureForm,
    OrderForm,
)

from django.forms.formsets import formset_factory

import datetime
import pytz
import base64


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
            imagef = form.cleaned_data["picture"]
            encoded_string = base64.b64encode(imagef.read())
            image = Image.objects.create(
                user=request.user,
                order=order,
                image=encoded_string,
                mimetype="0",
                image_type=0,
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

    OrderFormSet = formset_factory(OrderForm)

    if not request.user.is_authenticated:
        return redirect('friendship:login')
    elif request.method != 'POST':
        formset = OrderFormSet()
        primary_address = ShippingAddress.objects.filter(
            user=request.user
        ).filter(
            primary=True
        )
        if primary_address:
            address = primary_address[0]
        else:
            address = None
        return render(request,
                      'friendship/receiver_landing.html',
                      {'address': address, 'formset': formset, },
                      )
    else:
        req = request.POST
        fs = OrderFormSet(req)
        if not fs.is_valid()or int(request.POST['form-TOTAL_FORMS']) == 0:
            error(request, "You made a mistake in your form.")
            return redirect('friendship:receiver_landing')
        num = req['form-TOTAL_FORMS']
        orders = {}
        for i in range(int(num)):
            order = Order.objects.create(
                url=req['form-' + str(i) + '-url'],
                merchandise_type=req['form-' + str(i) + '-merchandise_type'],
                quantity=int(req['form-' + str(i) + '-quantity']),
                description=req['form-' + str(i) + '-description'],
                receiver=request.user,
                receiver_address=ShippingAddress.objects.
                    filter(user=request.user).
                    filter(primary=True)[0],
                bid_end_datetime=datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
                                 + datetime.timedelta(hours=int(req['form-' + str(i) + '-quantity'])),
            )
            action = OrderAction.objects.create(
                order=order,
                action=OrderAction.Action.ORDER_PLACED,
            )
            orders[i] = order

        return render(request, 'friendship/place_order_landing.html', {'orders': orders})