from django import forms
from marketing_manager.models import FAQ


class FAQEditForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['inner_HTML']

        widgets = {
            'inner_HTML': forms.Textarea(
                attrs={
                    'rows': 20,
                    'placeholder': 'Name*',
                    'class': 'input form-control',
                }
            ),
        }
