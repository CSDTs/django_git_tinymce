from django.db import models
from django.conf import settings


class Repo(models.Model):
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True, through='django_git_tinymce.Ownership', related_name='owners')


class Document(models.Model):
    repo = models.ForeignKey(Repo)
    url = models.CharField(max_length=255, null=True, blank=True)


class Ownership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    repo = models.ForeignKey('django_git_tinymce.Repo')
