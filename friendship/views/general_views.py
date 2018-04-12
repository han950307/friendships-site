
from django.shortcuts import render


def index(request, **kwargs):
    """
    Our homepage!
    """
    return render(request, 'friendship/index.html', **kwargs)


def testing(request):
    return render(request, 'friendship/testing.html', {})


def how_it_works(request):
    return render(request, 'friendship/how_it_works.html', {})


def about_us(request):
	return render(request, 'friendship/about_us.html', {})
