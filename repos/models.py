from django.db import models
from django.conf import settings
from django.core.files import File
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from django.urls import reverse
from django.utils.text import slugify

import os
import random
from PIL import Image
from shutil import rmtree

import pygit2
import time
from pygit2 import init_repository

def img_upload_location(instance, filename):
    return "{}/{}/{}".format(instance.owner, instance.slug, filename)

class RepositoryManager(models.Manager):
    def display_user_repo(self):
        pass


class Repository(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=200, blank=True, null=False)
    slug = models.SlugField(max_length=100)  # default max_length=50
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    image = models.ImageField(
        upload_to=img_upload_location,
        width_field='width',
        height_field='height',
        null=True,
        blank=True
    )
    height = models.CharField(max_length=10, null=True)
    width = models.CharField(max_length=10, null=True)
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
        return os.path.join(settings.REPO_DIR, self.owner.username, str(self.pk))


def create_thumbnail(media_path, instance, owner_name, max_length, max_width):
    filename = os.path.basename(media_path)
    thumb = Image.open(media_path)
    size = (max_length, max_width)
    thumb.thumbnail(size, Image.ANTIALIAS)
    temp_loc = "%s/%s/tmp" %(settings.MEDIA_ROOT, owner_name)
    if not os.path.exists(temp_loc):
        os.makedirs(temp_loc)
    temp_file_path = os.path.join(temp_loc, filename)
    if os.path.exists(temp_file_path):
        temp_path = os.path.join(temp_loc, "%s" %(random.random()))
        os.makedirs(temp_path)
        temp_file_path = os.path.join(temp_path, filename)

    temp_image = open(temp_file_path, "w")
    thumb.save(temp_image)
    thumb_data = open(temp_file_path, "rb")

    thumb_file = File(thumb_data)
    instance.image.save(filename.encode('ascii','ignore'), thumb_file)
    shutil.rmtree(temp_loc, ignore_errors=True)
    return True


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


@receiver(post_save, sender=Repository, dispatch_uid="path.to.this.module")
def repository_post_save(sender, instance, **kwagrs):
    print('***************post save **************')
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
        # bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        t = bld.write()
        repo.index.read()
        repo.index.add(fn)
        repo.index.write()
        # head = repo.lookup_reference('HEAD').resolve()
        c = repo.create_commit('HEAD', s, s, 'Initialized repo with a README.md', t, [])

    # if instance.image:
    #     img_max_size = (400, 300)

    #     media_path = instance.image.path
    #     owner = instance.owner
    #     create_thumbnail(media_path, instance, owner, img_max_size[0], img_max_size[1])


@receiver(post_delete, sender=Repository)
def repository_post_delete(sender, instance, **kwargs):
    path = instance.get_repo_path()
    try:
        rmtree(path)
    except:
        pass  # for now


class ForkedRepository(models.Model):
    original = models.ForeignKey(Repository, related_name='original_repo', blank=True, null=True)
    fork = models.ForeignKey(Repository)

    def save(self, *args, **kwargs):
        if not self.id:
            super(ForkedRepository, self).save(*args, **kwargs)
        # process self.parent_subject (should be called ...subjects, semantically)
        super(ForkedRepository, self).save(*args, **kwargs)
