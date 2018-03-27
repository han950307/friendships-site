

from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)

from ..models import Message


def send_message(request, orderID, asdf):
    """
    Process registration and put user data into the database.
    """
    # Trying to get the items.
    print("MADE IT HERE")
    try:
        text = request.POST['message']
    except KeyError:
        error(request, 'You did not fill out a field.')
        return redirect('friendship:index')
    else:
        message = Message.objects.create(
            author=request.user,
            transaction=orderID,
            content=text,
        )
        return redirect('friendship:index')