from django.forms import (
    Form,
    ModelForm,
    ImageField,
    Textarea,
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
        fields = ['url', 'merchandise_type', 'quantity', 'description', 'bid_end_datetime', ]
        common_settings = {'class': 'input form-control', 'required': 'required', }
        widgets = {
            'url': URLInput(attrs={**common_settings, **{'placeholder': 'URL'}}),
            'merchandise_type': Select(attrs={**common_settings, **{'placeholder': 'Category', }}),
            'quantity': NumberInput(attrs={**common_settings, **{'placeholder': 'Quantity', }}),
            'description': Textarea(attrs={**common_settings, **{'placeholder': ' Item Description + Promotion Code (i.e. size, color, style, etc.)'}}),
            'bid_end_datetime': NumberInput(attrs={**common_settings, **{'placeholder': '# Hours To Bid',
                                                                         'type': 'range',
                                                                         'step': '1',
                                                                         'min': '3',
                                                                         'max': '24',
                                                                         }}),
        }

    def is_valid(self):
        return super(OrderForm, self).is_valid()\
               and int(self.cleaned_data['merchandise_type']) != -1\
               and int(self.cleaned_data['quantity']) > 0

    def full_clean(self):
        super(OrderForm, self).full_clean()
        if 'bid_end_datetime' in self.errors:
            del self.errors['bid_end_datetime']
        # if not self.cleaned_data:
        #     return
        # if self.cleaned_data.get('bid_end_datetime') and 'bid_end_datetime' in self._errors:
        #     del self._errors['bid_end_datetime']
        # print(self.errors)
        # return self.cleaned_data

