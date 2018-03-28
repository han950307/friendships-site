
from django.http import HttpResponse

from django.core import serializers

from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

from .order_views import order_details

from ..models import (
    Message,
    Order,
)


def send_message(request, orderID):
    """
    Send message
    """
    try:
        text = request.POST['message']
    except KeyError:
        return order_details(request, orderID)
    else:
        if len(text) != 0:
            message = Message.objects.create(
                author=request.user,
                transaction=Order.objects.get(pk=orderID),
                content=text,
            )
        return order_details(request, orderID)


def sync_message(request, orderID):
    order = Order.objects.get(pk=orderID)
    if order.receiver != request.user and order.shipper != request.user:
        error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')
    messages = Message.objects.filter(transaction=order)
    return HttpResponse(serializers.serialize('json', messages))