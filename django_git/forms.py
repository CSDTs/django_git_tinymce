from django import forms 

from repos.models import Repository

class RepositoryModelForm(forms.ModelForm):
	class Meta:
		model = Repository
		fields = ['name', 'description']

		widgets = {
			"name": forms.TextInput(attrs={"placeholder": "Repository name"}),
			"description": forms.Textarea(attrs={"placeholder": "Repository description"})
		}