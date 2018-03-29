from django.forms import (
    Form,
    ModelForm,
    ImageField,
)
from friendship.models import Order


class UploadPictureForm(Form):
    picture = ImageField()


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['url', 'merchandise_type', 'bid_end_datetime', 'description', 'quantity']