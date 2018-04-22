
from django.shortcuts import render, redirect
import urllib

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


def change_locale(request, locale, next_url, **kwargs):
    request.session['locale'] = locale
    return redirect(urllib.parse.unquote(next_url), **kwargs)


def become_a_sender(request):
    return render(request, 'friendship/become_a_sender.html', {})


def contact_us(request):
    return render(request, 'friendship/contact_us.html', {})


def terms_of_use(request):
    return render(request, 'friendship/terms_of_use.html', {})
