from django import forms

class DataFileForm(forms.Form):
    file = forms.FileField()


class UploadFileForm(forms.Form):
    file = forms.FileField()