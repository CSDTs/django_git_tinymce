from django import forms
from tinymce.widgets import TinyMCE


class TinyMCEForm(forms.Form):
    content = forms.CharField(widget=TinyMCE(mce_attrs={'width': '100%'}))
