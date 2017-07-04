from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_init, post_delete
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify

from gitusers.models import Owner

from pygit2 import init_repository
from os.path import join
from shutil import rmtree

class RepositoryManager(models.Manager):
	def display_user_repo(self):
		pass

class Repository(models.Model):
	name = models.CharField(max_length=100, blank=False, null=False)
	description = models.CharField(max_length=200, blank=True, null=False)
	slug = models.SlugField() # default max_length=50
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	owner = models.ForeignKey(settings.AUTH_USER_MODEL)
	editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='editors', blank=True)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('gitusers:repo_detail', 
			kwargs={"username": self.owner, "slug": self.slug})

# class Owner(models.Model):
#     repo = models.ManyToManyField(Repository)
#     name = models.CharField(max_length=100)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL)

#     def __str__(self):
#         return self.name

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
		# exists = Repository.objects.filter(slug=slug).exists()
		# if exists:
		# 	slug = "{}-{}".format(slugify(instance.name), instance.timestamp.strftime("%Y%m%d%H%M%S"))
		instance.slug = slug


@receiver(post_save, sender=Repository)
def repository_post_init(sender, instance, **kwargs):
	path = join(settings.REPO_DIR, instance.slug)
	repo = init_repository(path)
	print(repo.is_empty)


@receiver(post_delete, sender=Repository)
def repository_post_delete(sender, instance, **kwargs):
	path = join(settings.REPO_DIR, instance.name)
	try:
		rmtree(path)
	except:
		pass #for now