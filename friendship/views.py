from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import User
from .models import UserInfo


# Create your views here.
def index(request):
    user_list = UserInfo.objects.all().select_related()
    output = ', '.join([q.email for q in user_list])
    return HttpResponse(output)
