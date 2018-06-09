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
            if x != ShipperInfo.ShipperType.FRIENDSHIP_BIDDER and
            x != ShipperInfo.ShipperType.FLIGHT_ATTENDANT
        ]
    )


class TravelerRegistrationForm(forms.Form):
    phone_number = forms.CharField(max_length=50)
    id_image = forms.ImageField()


class ShippingCompanyRegistrationForm(forms.Form):
    phone_number = forms.CharField(max_length=50)
    name = forms.CharField(max_length=200)


class FlightAttendantRegistrationForm(forms.Form):
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

    item_image_url = forms.CharField(required=False, max_length=3000, widget=forms.TextInput(attrs={
        'class': 'input form-control',
    }))

    item_image = forms.ImageField(
        required=False,
    )

    bid_trickle = forms.BooleanField(
        required=False,
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
                'data-validation': 'required',
            }
        ),
    )
    num_hours = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                'required': 'required',
                'class': 'num-hours',
                'checked': 'false',
                'data-validation': 'required',
            }
        ),
        choices=[
            (8, "8 hours"),
            (24, "24 hours"),
            (72, "72 hours"),
        ]
    )
    referrer = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Referrer Code',
                'class': 'input form-control',
                'data-validation': 'required',
            }
        ),
        required=False,
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
                    'data-validation': 'required',
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
                    'data-validation': 'required',
                }
            ),
            'color': forms.TextInput(
                attrs={
                    'placeholder': 'Color',
                    'class': 'input form-control',
                    'data-validation': 'required',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Additional Information (details, promo code, etc)',
                    'class': 'input form-control',
                    'rows': 5,
                    'data-validation': 'required',
                }
            ),
        }

    def is_valid(self):
        return super(OrderForm, self).is_valid()\
               and int(self.cleaned_data['merchandise_type']) != -1\
               and int(self.cleaned_data['quantity']) > 0

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            super().__init__(*args, initial=kwargs['initial'])
        else:
            super().__init__(*args)
        self.locale = kwargs['locale']
        if self.locale == "th_TH":
            self.fields["url"].widget.attrs['placeholder'] = "ลิ้งค์ URL*"
            self.fields["quantity"].widget.attrs['placeholder'] = "จำนวน*"
            self.fields["merchandise_type"].widget.attrs['placeholder'] = "เลือก*"
            self.fields["size"].widget.attrs['placeholder'] = "ขนาด"
            self.fields["color"].widget.attrs['placeholder'] = "สี"
            self.fields["num_hours"].choices = [
                (8, "8 ชั่วโมง"),
                (24, "24 ชั่วโมง"),
                (72, "72 ชั่วโมง"),
            ]
            self.fields["description"].widget.attrs['placeholder'] = "ข้อมูลเพิ่มเติมของสินค้า (รายละเอียดเพิ่มเติม, รหัสโปรโมชั่น, และอื่นๆ)"


class ManualWireTransferForm(forms.Form):
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


class ConfirmBanknoteForm(forms.Form):
    is_ok = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                'required': 'required',
                'checked': 'false',
            }
        ),
        choices=[
            (True, "Confirm"),
            (False, "Reject"),
        ]
    )


class UploadTrackingNumberForm(forms.Form):
    tracking_number = forms.CharField(max_length=140)
    provider = forms.CharField(max_length=450)


class UploadItemPurchasedReceiptForm(forms.Form):
    picture = forms.ImageField()


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'name',
            'address_line_1',
            'address_line_2',
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
                    'placeholder': 'Address Line 1*',
                    'class': 'input form-control',
                }
            ),
            'address_line_2': forms.TextInput(
                attrs={
                    'placeholder': 'Address Line 2',
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

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs:
            instance = kwargs["instance"]
        else:
            instance = None
        super().__init__(*args, instance=instance)
        self.locale = kwargs["locale"]
        if self.locale == "th_TH":
            self.fields["name"].widget.attrs['placeholder'] = "ชื่อ นามสกุล*"
            self.fields["address_line_1"].widget.attrs['placeholder'] = "บ้านเลขที่ หมู่*"
            self.fields["address_line_2"].widget.attrs['placeholder'] = "แขวง / ตำบล*"
            self.fields["city"].widget.attrs['placeholder'] = "เขต / อำเภอ*"
            self.fields["region"].widget.attrs['placeholder'] = "จังหวัด*"
            self.fields["postal_code"].widget.attrs['placeholder'] = "รหัสไปรษณีย์*"
            self.fields["country"].widget.attrs['placeholder'] = "ประเทศ*"
            self.fields["phone"].widget.attrs['placeholder'] = "เบอร์โทร*"
