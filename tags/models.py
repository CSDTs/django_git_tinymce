from django.db import models
from django.db.models.signals import pre_save, post_save, post_init, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.

from repos.models import Repository

class Tag(models.Model):
	title = models.CharField(max_length=100, unique=True)
	repos = models.ManyToManyField(Repository, blank = True)
	slug = models.SlugField(unique=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('detail', args=[self.slug])

@receiver(pre_save, sender=Tag)
def tag_pre_save(sender, instance, **kwargs):
	if not instance.slug:
	# Converts spaces to hyphens. Removes characters that aren’t alphanumerics, 
	# underscores, or hyphens. Converts to lowercase. Also strips leading and 
	# trailing whitespace.
	# "Joel is a slug" --> "joel-is-a-slug"
		slug = slugify(instance.name)
		instance.slug = slug