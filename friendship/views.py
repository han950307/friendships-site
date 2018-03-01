from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from .models import UserInfo


# Create your views here.
def index(request):
    user_list = UserInfo.objects.all()
    template = loader.get_template('friendship/index.html')
    context = {
        'user_list': user_list,
    }
    return HttpResponse(template.render(context, request))
