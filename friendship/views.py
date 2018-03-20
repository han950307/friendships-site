from django.conf import settings
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.contrib.auth.models import User
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect
)
from django.contrib.messages import error
from django.shortcuts import (
    get_object_or_404,
    render,
    redirect,
)
from django.template import loader
from django.urls import reverse
from django.views import generic

from .models import UserInfo, Order, Image, Bid

import datetime
import re

# Create your views here.
def get_min_bid(order):
    """
    Given an order, returns the min bid.
    """
    bids = Bid.objects.filter(order=order)
    min_arr = [x.bid_amount for x in bids]
    if min_arr:
        min_bid = min(min_arr)
    else:
        min_bid = "No current bids"
    return min_bid


def index(request, **kwargs):
    """
    Our homepage!
    """
    return render(request, 'friendship/index.html', **kwargs)


def order_details(request, pk):
    """
    Given the order_id (pk), displays its info.
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        order = Order.objects.get(pk=pk)
        receiver_info = UserInfo.objects.get(pk=order.receiver.id)
        return render(request, 'friendship/order_details.html', {
            'order': order,
            'receiver_info': receiver_info
        })


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
        return render(request, 'friendship/receiver_landing.html', {})
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


def register(request):
    """
    Load the registration page
    """
    return render(request, 'friendship/register.html', {})


def register_process(request):
    """
    Process registration and put user data into the database.
    """
    # Trying to get the items.
    try:
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        address = request.POST['address']
        phone = request.POST['phone']
    except KeyError:
        error(request, 'You did not fill out a field.')
        return render(request, 'friendship/register.html', {})
    else:
        # hack for generating a username from email.
        user = User.objects.create_user(
            re.sub(r"@|\.", r"", email),
            email,
            password
        )
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.is_superuser = False
        user.is_staff = False
        user.is_active = True
        user.save()

        user_id = user.id
        user_info = UserInfo.objects.create(
            shipping_address=address,
            phone=phone,
            is_receiver=True,
            is_shipper=True,
            user=user
        )
        return redirect('friendship:login')


def login_view(request):
    """
    load login view.
    """
    return render(request, 'friendship/login.html', {})


def login_process(request):
    """
    Process login
    """
    try:
        # hack for generating a username from email
        username = re.sub(r"@|\.", r"", request.POST['email'])
        password = request.POST['password']
    except KeyError:
        return render(request, 'friendship/login.html', {
            error(request, 'You didn\'t fill out something')
        })
    else:
        # Use username to authenticate. LOL this is so bad
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(request.session.__dict__)
            request.session['logged_on'] = True
            return HttpResponseRedirect(reverse('friendship:index'))
        else:
            error(request, 'Did not find a match.')
            return render(request, 'friendship/login.html', {})


def open_orders(request, filter):
    """
    View currently open orders.
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        user_info = UserInfo.objects.get(pk=request.user.id)
        if not user_info.is_shipper:
            error(request, 'You do not have permissions to access this page.')
            return redirect('friendship:index')

        # Only display orders within a day ago.
        timelim = datetime.datetime.now() - datetime.timedelta(days=1)
        qset = Order.objects.filter(date_placed__gte=timelim)

        # Get minimum bid.
        for order in qset:
            order.min_bid = get_min_bid(order)

        return render(request, 'friendship/open_orders.html', {
            'orders': qset
        })


def make_bid(request, order_id):
    """
    Make bid view. Allows sender to make a bid for the order.
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        user_info = UserInfo.objects.get(pk=request.user.id)
        if not user_info.is_shipper:
            error(request, 'You do not have permissions to access this page.')
            return redirect('friendship:index')
        order = Order.objects.get(pk=order_id)
        return render(request, 'friendship/make_bid.html', {'order' : order})


def make_bid_process(request, order_id):
    """
    Processes make bid
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        user_info = UserInfo.objects.get(pk=request.user.id)
        # Must be a shipper.
        if not user_info.is_shipper:
            error(request, 'You do not have permissions to access this page.')
            return redirect('friendship:index')
        bid_amount = request.POST["bid_amount"]
        order = Order.objects.get(pk=order_id)
        Bid.objects.create(
            bid_amount=bid_amount,
            order=order,
            shipper_id=request.user.id,
        )

        # Just return another view after processing it.
        return open_orders(request, "recent")


def logout_view(request):
    """
    Logs a user out :P
    """
    logout(request)
    error(request, 'Successfully Logged out.')
    return redirect('friendship:login')


def testing(request):
    return render(request, 'friendship/testing.html', {})
