
from django.shortcuts import render, redirect
from friendsite import settings
import urllib

def index(request, **kwargs):
    """
    Our homepage!
    """
    if 'locale' not in request.session:
        request.session['locale'] = 'en_US'
    request.session["dev"] = settings.DEBUG
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


def privacy_policy(request):
    return render(request, 'friendship/privacy_policy.html', {})
