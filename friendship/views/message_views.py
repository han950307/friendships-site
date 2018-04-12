from django.contrib.auth.decorators import login_required
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


@login_required
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


@login_required
def sync_message(request, order_id):
    order = Order.objects.get(pk=order_id)
    if order.receiver != request.user and order.shipper != request.user:
        error(request, 'You\'ve got the wrong user')
        return redirect('friendship:index')
    messages = Message.objects.filter(transaction=order);
    return HttpResponse(serializers.serialize('json', messages))


@login_required
def messages(request):
    qset = Order.objects.filter(receiver=request.user).union(Order.objects.filter(shipper=request.user))
    return render(request, 'friendship/messages.html', {
        'orders': qset,
    })