from datetime import datetime

from django import forms

from tinymce.widgets import TinyMCE

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

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request')
		super(RepositoryModelForm, self).__init__(*args, **kwargs)


	def clean_name(self):
		name = self.cleaned_data.get('name')
		query_set = Repository.objects.filter(name=name, owner=self.request.user)

		if query_set.exists():
			raise forms.ValidationError("Repository named '{}' already exists".format(name))

		return name



class TinyMCEFileEditForm(forms.Form):
    content = forms.CharField(widget=TinyMCE(mce_attrs={'width': 800}))
    commit_message = forms.CharField(required=False, empty_value="Edited on {}".format(datetime.now().strftime("%A, %d. %B %Y %I:%M%p")))