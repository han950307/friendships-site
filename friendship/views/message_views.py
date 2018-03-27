
from django.http import HttpResponse

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
        error(request, 'You did not fill out a field.')
        return order_details(request, orderID)
    else:
        message = Message.objects.create(
            author=request.user,
            transaction=Order.objects.get(pk=orderID),
            content=text,
        )
        return order_details(request, orderID)
