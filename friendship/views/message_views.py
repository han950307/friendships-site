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


def send_message(request, order_id):
    """
    Send message
    """
    try:
        text = request.POST['message']
    except KeyError:
        return order_details(request, order_id)
    else:
        if len(text) != 0:
            message = Message.objects.create(
                author=request.user,
                transaction=Order.objects.get(pk=order_id),
                content=text,
            )
        return order_details(request, order_id)


def sync_message(request, order_id, after=0):
    order = Order.objects.get(pk=order_id)
    if order.receiver != request.user and order.shipper != request.user:
        error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')
    messages = reversed(Message.objects.filter(transaction=order))
    return HttpResponse(serializers.serialize('json', messages))
