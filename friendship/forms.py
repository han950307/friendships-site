from django import forms


class UploadPictureForm(forms.Form):
	picture = forms.ImageField()
