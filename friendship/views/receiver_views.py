
from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

from ..models import Order

def receiver_landing_view(request):
    """
    This is a page for a form for making an order.
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        return render(request, 'friendship/receiver_landing.html', {})


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
            if (merchandise_type == "shoes"):
                thetype = 1
            else:
                thetype = 0
            desc = request.POST['desc']
        except (KeyError, ValueError):
            error(request, 'You didn\'t fill out something or you' + \
                ' didn\'t enter a value for quantity.')
            return render(request, 'friendship/place_order.html', {})
        else:
            order = Order.objects.create(
                url=url,
                merchandise_type=thetype,
                status=0,
                quantity=quantity,
                description=desc,
                receiver=request.user,
            )
            return render(request, 'friendship/place_order_landing.html', {'order': order})