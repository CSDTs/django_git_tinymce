
from django import forms

class CreateRepo(forms.Form):
    repositoryName = forms.CharField(max_length=100, label='Repository Name')
    repositoryDesc = forms.CharField(max_length=200, label='Repository Desc', required=False)