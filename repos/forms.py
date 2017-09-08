from datetime import datetime

from django import forms
from django.utils.text import slugify

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
		name = self.cleaned_data['name']
		query_set = Repository.objects.filter(
			name=name,
			owner=self.request.user
		)

		if query_set.exists():
			raise forms.ValidationError(
				"Repository named '{}' already exists".format(name)
			)

		slugified = slugify(name)
		if Repository.objects.filter(
			slug=slugified, owner=self.request.user).exists():
			raise forms.ValidationError(
				"Slugified repo named '{}' already exists".format(slugified)
			)

		return name


class RepositoryUpdateModelForm(forms.ModelForm):
	tags = forms.CharField(label='Related tags', required=False)
	request = None
	old_name = None

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
		self.old_name = kwargs.pop('old_name')
		super(RepositoryUpdateModelForm, self).__init__(*args, **kwargs)

	def clean_name(self):
		name = self.cleaned_data['name']
		if not name == self.old_name:
			query_set = Repository.objects.filter(
				name=name,
				owner=self.request.user
			)

			if query_set.exists():
				raise forms.ValidationError(
					"Repository named '{}' already exists".format(name)
				)

			slugified = slugify(name)
			if Repository.objects.filter(
				slug=slugified, owner=self.request.user).exists():
				raise forms.ValidationError(
					"Slugified repo named '{}' already exists".format(slugified)
				)
				

		return name


class TinyMCEFileEditForm(forms.Form):
	content = forms.CharField(widget=TinyMCE(mce_attrs={'width': 800}))
	commit_message = forms.CharField(
		required=False,
		empty_value="edited on {}".format(
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
		filename = self.cleaned_data['filename']
		if filename == ('.html'.strip()):
			raise forms.ValidationError(
				'Please enter file name, i.e. "example.html"'
			)

		return filename


class FileRenameForm(forms.Form):
	# old_filename = forms.CharField(label='File name', required=True)
	new_filename = forms.CharField(label='New file name', required=True)
	commit_message = forms.CharField(
		required=False,
		empty_value="Created on {}".format(
			datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
		)
	)
	def clean_filename(self):
		new_filename = self.cleaned_data['new_filename']
		if new_filename == ('.html'.strip()):
			raise forms.ValidationError(
				'Please enter file name, i.e. "example.html"'
			)

		return new_filename

class RepoForkRenameForm(forms.Form):
	# old_filename = forms.CharField(label='File name', required=True)
	new_reponame = forms.CharField(label='New fork name', required=True)
	def clean_filename(self):
		new_reponame = self.cleaned_data['new_reponame']

		return new_reponame
