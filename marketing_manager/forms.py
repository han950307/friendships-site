from django import forms
from marketing_manager.models import FAQ


class FAQEditForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['inner_HTML', 'inner_HTML_thai']

        widgets = {
            'inner_HTML': forms.Textarea(
                attrs={
                    'rows': 20,
                    'placeholder': 'Some English FAQ',
                    'class': 'input form-control',
                }
            ),
            'inner_HTML_thai': forms.Textarea(
                attrs={
                    'rows': 20,
                    'placeholder': 'Some Thai Translation of FAQ',
                    'class': 'input form-control',
                }
            ),
        }
