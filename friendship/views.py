from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import UserInfo


# Create your views here.
def index(request):
    print(settings.AUTH_USER_MODEL)
    user_list = UserInfo.objects.all().select_related()
    output = ', '.join([q.user.email for q in user_list])
    return HttpResponse(output)
