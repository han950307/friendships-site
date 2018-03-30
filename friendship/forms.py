from django.forms import (
    Form,
    ModelForm,
    ImageField,
    TextInput,
    NumberInput,
    URLInput,
    Select,
)
from friendship.models import Order


class UploadPictureForm(Form):
    picture = ImageField()


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['url', 'merchandise_type', 'bid_end_datetime', 'description', 'quantity']
        widgets = {
            'url': URLInput(attrs={'class': 'input form-control col-sm-6'}),
            'merchandise_type': Select(attrs={'class': 'input form-control col-sm-6'}),
            'bid_end_datetime': NumberInput(attrs={'class': 'input form-control col-sm-6'}),
            'description': TextInput(attrs={'class': 'input form-control col-sm-6'}),
            'quantity': NumberInput(attrs={'class': 'input form-control col-sm-6'}),
        }