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

from .models import UserInfo, Order, Image

import re

# Create your views here.
def index(request, **kwargs):
    return render(request, 'friendship/index.html', **kwargs)


class OrderDetailView(generic.DetailView):
    """
    Should show details of the order with items and stuff.
    """
    model = Order


# class DetailsView(generic.DetailView):
#     model = UserInfo
#     template_name = 'friendship/details.html'


class ItemDetailView(generic.DetailView):
    """
    Should show details of the item itself.
    """
    pass


class SenderDashboard(generic.ListView):
    """
    Should show a list of accepted items, its progress
    Also items that they can accept.
    """
    pass


class ReceiverDashboard(generic.ListView):
    """
    Should show a list of requested items and summary and a history of items.
    """
    template_name = 'friendship/sender'
    context_object_name = 'order_list'

    def get_queryset(self):
        # TODO implement filter
        return Order.objects.filter();


def place_order_view(request):
    """
    Form
    """
    if not request.user.is_authenticated:
        error(request, 'You must login first to access this page.')
        return redirect('friendship:login')
    else:
        return render(request, 'friendship/place_order.html', {})


def place_order_process(request):
    """
    processing inputs.
    """
    # render view for returning to dashboard or requesting another item
    pass


def register(request):
    """
    Load the registration page
    """
    return render(request, 'friendship/register.html', {})


def register_process(request):
    """
    Process registration and put user data into the database.
    """
    try:
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        address = request.POST['address']
        phone = request.POST['phone']
    except KeyError:
        return render(request, 'friendship/register.html', {
            error(request, 'You didn\'t fill out something.')
        })
    else:
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
            is_shipper=False,
            user_id=user_id
        )
        return HttpResponseRedirect(reverse('friendship:login'))


def login_view(request):
    return render(request, 'friendship/login.html', {})


def login_process(request):
    try:
        username = re.sub(r"@|\.", r"", request.POST['email'])
        password = request.POST['password']
    except KeyError:
        return render(request, 'friendship/login.html', {
            error(request, 'You didn\'t fill out something')
        })
    else:
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(request.session.__dict__)
            request.session['logged_on'] = True
            return HttpResponseRedirect(reverse('friendship:index'))
        else:
            return render(request, 'friendship/login.html', {
                error(request, 'Did not find a match.')
            })


def logout_view(request):
    logout(request)
    error(request, 'Successfully Logged out.')
    return redirect('friendship:login')
