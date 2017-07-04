from django import forms 

from .models import Repository

class RepositoryModelForm(forms.ModelForm):
	tags = forms.CharField(label='Related tags', required=False)
	class Meta:
		model = Repository
		fields = ['name', 'description']

		widgets = {
			"name": forms.TextInput(attrs={"placeholder": "Repository name"}),
			"description": forms.Textarea(attrs={"placeholder": "Repository description"})
		}