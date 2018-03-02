from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import generic

from .models import UserInfo


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'friendship/index.html'
    context_object_name = 'user_list'

    def get_queryset(self):
        return UserInfo.objects.all()


class DetailsView(generic.DetailsView):
    model = UserInfo
    template_name = 'friendship/details.html'


def register(request):
    return render(request, 'friendship/register.html', {})


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
