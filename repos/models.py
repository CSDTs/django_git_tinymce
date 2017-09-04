from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from django.urls import reverse
from django.utils.text import slugify

import os
from os.path import join
from shutil import rmtree

import pygit2
import time
from pygit2 import init_repository


class RepositoryManager(models.Manager):
	def display_user_repo(self):
		pass


class Repository(models.Model):
	name = models.CharField(max_length=100, blank=False, null=False)
	description = models.CharField(max_length=200, blank=True, null=False)
	slug = models.SlugField(max_length=100)  # default max_length=50
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	editors = models.ManyToManyField(
		settings.AUTH_USER_MODEL, related_name='editors', blank=True)

	def __str__(self):
		return "{} - {}".format(self.name, self.owner.username)

	def get_absolute_url(self):
		return reverse(
			'gitusers:repo_detail',
			kwargs={"username": self.owner, "slug": self.slug})

	def get_repo_path(self):
		return join(settings.REPO_DIR, self.owner.username, str(self.pk))


# Django Signals
# https://docs.djangoproject.com/en/1.11/ref/signals/#post-save


@receiver(pre_save, sender=Repository)
def repository_pre_save(sender, instance, **kwargs):
	if not instance.slug:
		# Converts spaces to hyphens. Removes characters that aren’t alphanumerics,
		# underscores, or hyphens. Converts to lowercase. Also strips leading and
		# trailing whitespace.
		# "Joel is a slug" --> "joel-is-a-slug"
		slug = slugify(instance.name)
		instance.slug = slug


@receiver(post_save, sender=Repository)
def repository_post_save(sender, instance, **kwagrs):
	# init repo after model object created
	repo = init_repository(instance.get_repo_path())
	if repo.head_is_unborn:
		s = pygit2.Signature('Repo_Init', 'csdtrpi@gmail.com', int(time.time()), 0)
		print('instance', instance)
		print('sender', sender)
		print('repo', repo)
		data = '# {}'.format(instance)
		fn = 'README.md'
		bld = repo.TreeBuilder()
		f = open(os.path.join(repo.workdir, fn), 'w')
		f.write(data)
		f.close()
		b = repo.create_blob_fromworkdir(fn)
		bld = repo.TreeBuilder()
		bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode)
		t = bld.write()
		repo.index.read()
		repo.index.add(fn)
		repo.index.write()
		# head = repo.lookup_reference('HEAD').resolve()
		c = repo.create_commit('HEAD', s, s, 'Initialized repo with a README.md', t, [])


@receiver(post_delete, sender=Repository)
def repository_post_delete(sender, instance, **kwargs):
	path = instance.get_repo_path()
	try:
		rmtree(path)
	except:
		pass  # for now
