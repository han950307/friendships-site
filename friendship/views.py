from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


# Create your views here.
def index(request):
    user_list = settings.AUTH_USER_MODEL.objects.all()
    print(user_list)
    output = ', '.join([q.email for q in user_list])
    return HttpResponse(output)
