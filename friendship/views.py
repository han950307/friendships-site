from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from .models import UserInfo
from django.http import Http404
from django.shortcuts import get_object_or_404, render


# Create your views here.
def index(request):
    user_list = UserInfo.objects.all()
    return render(request, 'friendship/index.html', {'user_list': user_list})

def details(request, user_id):
    user = get_object_or_404(UserInfo, pk=user_id)
    return render(request, 'friendship/details.html', {'user_info': user})

def register(request):
    return render(request, 'friendship/register.html', {})

def register_process(request):
    email = request.POST['email']
