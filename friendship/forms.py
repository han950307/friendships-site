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
        common_settings = {'class': 'input form-control', 'required': 'required'}
        widgets = {
            'url': URLInput(attrs=common_settings),
            'merchandise_type': Select(attrs=common_settings),
            'bid_end_datetime': NumberInput(attrs=common_settings),
            'description': TextInput(attrs=common_settings),
            'quantity': NumberInput(attrs=common_settings),
        }