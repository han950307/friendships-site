
from django.shortcuts import render, redirect


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


def change_locale(request, locale):
	request.session['locale'] = locale
	return redirect('friendship:index')


def become_a_sender(request):
	return render(request, 'friendship/become_a_sender.html', {})
