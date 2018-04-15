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
from friendship.models import Order, ShipperInfo, ShippingAddress, Money


"""ACCOUNTS"""
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


class SenderRegistrationForm(forms.Form):
    shipper_type = forms.ChoiceField(
        widget=forms.Select,
        choices=[
            (x.value, x)
            for x
            in ShipperInfo.ShipperType
        ]
    )


class TravelerRegistrationForm(forms.Form):
    phone_number = forms.CharField(max_length=50)
    id_image = forms.ImageField()


class ShippingCompanyRegistrationForm(forms.Form):
    phone_number = forms.CharField(max_length=50)
    name = forms.CharField(max_length=200)


class BidForm(forms.Form):
    currency = forms.ChoiceField(
        choices=[
            (x.value, str(x).upper())
            for x
            in Money.Currency
            if x == Money.Currency.USD
        ],
        widget=forms.Select(
            attrs={
                'placeholder': 'Currency',
                'required': 'required',
                'class': 'input form-control',
                'data-validation': 'required',
            }
        ),
    )

    wages = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Shipping Bid (12.00)',
                'required': 'required',
                'class': 'input form-control',
                'data-validation': 'required',
            }
        )
    )

    retail_price = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Retail Price (125.00)',
                'required': 'required',
                'class': 'input form-control',
                'data-validation': 'required',
            }
        )
    )


"""ORDER RELATED FORMS"""
class OrderForm(forms.ModelForm):
    merchandise_type = forms.ChoiceField(
        choices=[
            (x.value, str(x).title())
            for x
            in Order.MerchandiseType
        ],
        widget=forms.Select(
            attrs={
                'placeholder': 'Category*',
                'required': 'required',
                'class': 'input input-group form-control',
            }
        ),
    )
    num_hours = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                'required': 'required',
                'class': 'num-hours',
                'checked': 'false',
            }
        ),
        choices=[
            (8, "8 hours"),
            (24, "24 hours"),
            (72, "72 hours"),
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
                    'placeholder': 'URL*',
                    'required': 'required',
                    'class': 'input form-control',
                    'data-validation': 'required',
                }
            ),
            'item_image': forms.FileInput(
                attrs={
                    'type': 'file',
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'placeholder': 'Quantity*',
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
                    'class': 'input form-control'
                }
            ),
        }

    def is_valid(self):
        return super(OrderForm, self).is_valid()\
               and int(self.cleaned_data['merchandise_type']) != -1\
               and int(self.cleaned_data['quantity']) > 0


class ManualWireTransferForm(forms.Form):
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
        widget=forms.FileInput(
            attrs={
                'data-validation': 'required',
                'data-validation-error-msg': 'Please upload an image.',
            }
        ),
    )


class UploadPictureForm(forms.Form):
    picture = forms.ImageField()


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'name',
            'address_line_1',
            'city',
            'region',
            'postal_code',
            'country',
            'phone',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Name*',
                    'class': 'input form-control',
                }
            ),
            'address_line_1': forms.TextInput(
                attrs={
                    'placeholder': 'Address*',
                    'class': 'input form-control',
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'placeholder': 'City*',
                    'class': 'input form-control',
                }
            ),
            'region': forms.TextInput(
                attrs={
                    'placeholder': 'Region*',
                    'class': 'input form-control',
                }
            ),
            'postal_code': forms.TextInput(
                attrs={
                    'placeholder': 'Postal Code*',
                    'class': 'input form-control',
                }
            ),
            'country': forms.TextInput(
                attrs={
                    'placeholder': 'Country*',
                    'class': 'input form-control',
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'placeholder': 'Phone*',
                    'class': 'input form-control',
                }
            ),
        }
