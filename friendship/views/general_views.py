
from django.shortcuts import render


def index(request, **kwargs):
    """
    Our homepage!
    """
    return render(request, 'friendship/index.html', **kwargs)


def testing(request):
    return render(request, 'friendship/testing.html', {})
