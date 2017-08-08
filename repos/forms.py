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
			"description": forms.Textarea(
				attrs={"placeholder": "Repository description"}
			)
		}

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request')
		super(RepositoryModelForm, self).__init__(*args, **kwargs)

	def clean_name(self):
		# name = self.cleaned_data.get('name')
		name = self.clean_data['name']
		query_set = Repository.objects.filter(
			name=name,
			owner=self.request.user
		)

		if query_set.exists():
			raise forms.ValidationError(
				"Repository named '{}' already exists".format(name)
			)

		return name


class TinyMCEFileEditForm(forms.Form):
	content = forms.CharField(widget=TinyMCE(mce_attrs={'width': 800}))
	commit_message = forms.CharField(
		required=False,
		empty_value="Edited on {}".format(
			datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
		)
	)


class FileCreateForm(forms.Form):
	filename = forms.CharField(label='File name', required=True)
	content = forms.CharField(widget=TinyMCE(mce_attrs={'width': 800}))
	commit_message = forms.CharField(
		required=False,
		empty_value="Created on {}".format(
			datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
		)
	)
	
	def clean_filename(self):
		filename = self.clean_data['filename']
		if filename == ('.html'.strip()):
			raise forms.ValidationError(
				'Please enter file name, i.e. "example.html"'
			)
		
		return filename
