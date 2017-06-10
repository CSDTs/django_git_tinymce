
from django import forms

class CreateRepo(forms.Form):
	repositoryName = forms.CharField(max_length=100, label='Repository Name')
	repositoryDesc = forms.CharField(max_length=200, label='Repository Desc', required=False)

class DeleteRepo(forms.Form):
	repositoryName = forms.CharField(max_length=100)

# Forms for changing repo name and desc
class RepoSettings(forms.Form):
	repositoryName = forms.CharField(max_length=100, label='Repository Name')
	repositoryDesc = forms.CharField(max_length=200, label='Repository Desc', required=False)