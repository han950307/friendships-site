from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import generic

from .models import UserInfo, Order, Image


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'friendship/index.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        return UserInfo.objects.all()


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


class SenderDashboard(generic.listView):
    """
    Should show a list of accepted items, its progress
    Also items that they can accept.
    """
    pass


class ReceiverDashboard(generic.listView):
    """
    Should show a list of requested items and summary and a history of items.
    """
    template_name = 'friendship/sender'
    context_object_name = 'order_list'

    def get_queryset(self):
        # TODO implement filter
        return Order.objects.filter();


def request_item(request):
    """
    Form
    """
    return render(request, 'friendship/request_item', {})


def request_item_process(request):
    """
    processing inputs.
    """
    # render view for returning to dashboard or requesting another item
    pass


def register(request):
    return render(request, 'friendship/register', {})


def register_process(request):
    try:
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        address = request.POST['address']
        phone = request.POST['phone']
    except KeyError:
        return render(request, 'friendship/register', {
                'error_message': "You didn't fill out something."
        })
    else:
        user = User.objects.create(
            password=password,
            is_superuser=False,
            first_name=firstname,
            last_name=lastname,
            email=email,
            is_staff=False,
            is_active=False,
        )
        user_id = user.id
        UserInfo.objects.create(
            shipping_address=address,
            phone=phone,
            is_receiver=True,
            is_sender=False,
            user_id=user_id
        )
        return HttpResponseRedirect(reverse('friendship:index'))
