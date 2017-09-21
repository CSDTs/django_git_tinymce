from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify


class TagManager(models.Manager):
    # Override all to only show active tags.
    def all(self):
        return super(TagManager, self).all().filter(active=True)

    # def get_xxx():
    #     pass


class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True)
    # repos = models.ManyToManyField(Repository, blank=True)
    slug = models.SlugField(unique=True)
    active = models.BooleanField(default=True)

    objects = TagManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tags:detail', args=[self.slug])


@receiver(pre_save, sender=Tag)
def tag_pre_save(sender, instance, **kwargs):
    if not instance.slug:
        # Converts spaces to hyphens. Removes characters that aren’t alphanumerics,
        # underscores, or hyphens. Converts to lowercase. Also strips leading and
        # trailing whitespace.
        # "Joel is a slug" --> "joel-is-a-slug"
        slug = slugify(instance.title)
        instance.slug = slug
