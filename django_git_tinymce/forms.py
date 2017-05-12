from django.forms import ModelForm
from django_git_tinymce.models import Document


class DocumentForm(ModelForm):

    class Meta:
        model = Document
        exclude = ('owners',)
