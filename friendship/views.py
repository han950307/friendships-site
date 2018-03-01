from django.shortcuts import render
from django.http import HttpResponse
from .models import User


# Create your views here.
def index(request):
    user_list = User.objects.all()
    output = ', '.join([q.email for q in user_list])
    return HttpResponse(output)
