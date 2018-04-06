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
from django import forms
from friendship.models import Order, ShipperInfo, ShippingAddress


class UploadPictureForm(forms.Form):
    picture = forms.ImageField()


class OrderForm(forms.ModelForm):
    num_hours = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                'required': 'required',
            }
        ),
        choices=[
            (6, "6 hours"),
            (14, "14 hours"),
            (24, "24 hours"),
        ]
    )
    class Meta:
        model = Order
        fields = [
            'url',
            'merchandise_type',
            'quantity',
            'description',
            'item_image',
            'size',
            'color',
        ]
        widgets = {
            'url': forms.URLInput(
                attrs={
                    'placeholder': 'URL',
                    'required': 'required',
                    'class': 'input form-control',
                }
            ),
            'item_image': forms.FileInput(),
            'merchandise_type': forms.Select(
                attrs={
                    'placeholder': 'Category',
                    'required': 'required',
                    'class': 'input form-control',
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'placeholder': 'Category',
                    'required': 'required',
                    'class': 'input form-control',
                    'min': 1
                }
            ),
            'size': forms.TextInput(
                attrs={
                    'placeholder': 'Size',
                    'class': 'input form-control',
                }
            ),
            'color': forms.TextInput(
                attrs={
                    'placeholder': 'Color',
                    'class': 'input form-control',
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'placeholder': 'Any other details about the item',
                    'class': 'input form-control',
                }
            ),
        }

    def is_valid(self):
        return super(OrderForm, self).is_valid()\
               and int(self.cleaned_data['merchandise_type']) != -1\
               and int(self.cleaned_data['quantity']) > 0


class ManualWireTransferForm(Form):
    account_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Account Number: 45674894512456',
                'data-validation': 'required',
                'class': 'input form-control',
                'data-validation-error-msg': 'Please enter your account number.',
            }
        ),
    )
    banknote_image = forms.ImageField(
        widget=forms.FileInput(),
    )


class SenderRegistrationForm(Form):
    shipper_type = forms.ChoiceField(
        widget=forms.Select,
        choices=[
            (x.value, x)
            for x
            in ShipperInfo.ShipperType
        ]
    )


class ShippingAddressForm(ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'name',
            'address_line_1',
            'address_line_2',
            'address_line_3',
            'city',
            'region',
            'postal_code',
            'country',
            'phone',
        ]
    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.__class__ == forms.widgets.TextInput:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' input'
                    field.widget.attrs['class'] += ' form-control'
                else:
                    field.widget.attrs.update({'class':'input form-control'})


class TravelerRegistrationForm(Form):
    phone_number = forms.CharField(max_length=50)
    id_image = forms.ImageField()


class ShippingCompanyRegistrationForm(Form):
    phone_number = forms.CharField(max_length=50)
    name = forms.CharField(max_length=200)


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'First Name *',
                'data-validation': 'required',
                'class': 'input form-control',
                'data-validation-error-msg': 'Please enter your first name.',
            }
        ),
    )
    last_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Last Name *',
                'data-validation': 'required',
                'class': 'input form-control',
                'data-validation-error-msg': 'Please enter your last name.',
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Email *',
                'data-validation': 'required',
                'class': 'input form-control',
                'data-validation-error-msg': 'Please enter your email address.',
            }
        ),
    )
    password = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password *',
                'data-validation': 'required',
                'class': 'input form-control',
                'data-validation-error-msg': 'Please enter your desired password.',
            }
        ),
    )
