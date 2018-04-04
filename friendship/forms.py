from django import forms
from django.forms import (
    Form,
    ModelForm,
    ImageField,
    Textarea,
    NumberInput,
    URLInput,
    Select,
    FileField,
)
from friendship.models import Order


class UploadPictureForm(Form):
    picture = ImageField()


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['url', 'merchandise_type', 'quantity', 'description', 'bid_end_datetime',] #'actions__action']
        common_settings = {'class': 'input form-control', 'required': 'required', }
        widgets = {
            'url': URLInput(attrs={**common_settings, **{'placeholder': 'URL'}}),
            'merchandise_type': Select(attrs={**common_settings, **{'placeholder': 'Category', }}),
            'quantity': NumberInput(attrs={**common_settings, **{'placeholder': 'Quantity',
                                                                 'min': '1',
                                                                 }}),
            'description': Textarea(attrs={**common_settings, **{'placeholder': ' Item Description + Promotion Code'}}),
            'bid_end_datetime': NumberInput(attrs={**common_settings, **{'placeholder': '# Hours To Bid',
                                                                         'type': 'range',
                                                                         'step': '1',
                                                                         'min': '3',
                                                                         'max': '24',
                                                                         }}),
            # 'actions__action': NumberInput(attrs=common_settings),
        }

    def is_valid(self):
        return super(OrderForm, self).is_valid()\
               and int(self.cleaned_data['merchandise_type']) != -1\
               and int(self.cleaned_data['quantity']) > 0

    def full_clean(self):
        super(OrderForm, self).full_clean()
        if 'bid_end_datetime' in self.errors:
            del self.errors['bid_end_datetime']


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=120)
    last_name = forms.CharField(max_length=120)
    email = forms.EmailField()
    password = forms.CharField(max_length=200, widget=forms.PasswordInput())
