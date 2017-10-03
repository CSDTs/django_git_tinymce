from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from django.urls import reverse
from django.utils.text import slugify

import os
from os.path import join
from shutil import rmtree

from . import imglib
from . import choices as c
from tags.models import Tag
import pygit2
import time
from pygit2 import init_repository


class RepositoryManager(models.Manager):
    def display_user_repo(self):
        pass


def my_awesome_upload_function(instance, filename):
    return os.path.join('profile/%s/' % instance.id, filename)


class Repository(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=200, blank=True, null=False)
    slug = models.SlugField(max_length=100)  # default max_length=50
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='editors', blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=my_awesome_upload_function)
    tags = models.ManyToManyField(Tag, blank=True, related_name="repos")
    grade_level = models.CharField(max_length=2, choices=c.GRADE_LEVEL, blank=True)
    subject = models.CharField(max_length=100, choices=c.SUBJECTS, blank=True)
    culture = models.CharField(max_length=100, choices=c.CULTURES, blank=False)

    def __str__(self):
        return "{} - {}".format(self.name, self.owner.username)

    def get_absolute_url(self):
        return reverse(
            'gitusers:repo_detail',
            kwargs={"username": self.owner, "slug": self.slug})

    def get_repo_path(self):
        return join(settings.REPO_DIR, self.owner.username, str(self.pk))

    def get_repo_path_media(self):
        print("******************", join(self.owner.username, str(self.pk)))
        return join(self.owner.username, str(self.pk))

    def save(self, *args, **kwargs):
        super(Repository, self).save(*args, **kwargs)
        if self.image:
            imglib.resize_image(self.image)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


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
        data = '<p><h1>{}</h1></p>'.format(instance)
        fn = 'README.html'
        f = open(os.path.join(repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        b = repo.create_blob_fromworkdir(fn)
        bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode )
        bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        bld.write()
        repo.index.read()
        repo.index.add(fn)
        repo.index.write()
        # head = repo.lookup_reference('HEAD').resolve()

        # Nav bar:
        data = """
        <nav class="navbar navbar-inverse navbar-local visible-xs">\
    <div class="container-fluid">\
    <div class="navbar-header">\
        <a class="navbar-brand" href="/{1}/{2}/render/index.html">{0}</a>
        <button aria-expanded="false" class="navbar-toggle collapsed"
        data-target="#nav-menu" data-toggle="collapse" type="button">
        <span class="sr-only">Toggle navigation</span> <span class="icon-bar">
        </span> <span class="icon-bar"></span> <span class="icon-bar">
        </span></button>\
    </div>\
    <div class="collapse navbar-collapse navbar-right" id="nav-menu">\
        <ul class="nav navbar-nav">\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/index.html">Background</a>\
            </li>\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/origins.html">Origins</a>\
            </li>\
            <li class="visible-xs">\
                <a href="/{1}/{2}/render/teaching.html">Teaching Materials</a>\
            </li>\
        </ul>\
\
    </div>\
    </div>\
</nav>\
\
\
<!-- sidebar -->\
        <div class="stuck">\
            <div class="col-xs-6 col-sm-3 sidebar-offcanvas" id="sidebar" role="navigation">\
                <ul class="nav">\
                    <li class="active"><a href="/{1}/{2}/render/index.html">Background</a></li>\
                    <li class="indented"><a href="/{1}/{2}/render/origins.html">Origins</a></li>\
                    <li><a href="/{1}/{2}/render/tutorial.html">Tutorial</a></li>\
                    <li><a href="/{1}/{2}/render/software.html">Software</a></li>\
                    <li><a href="/{1}/{2}/render/teaching.html">Teaching Materials</a></li>\
                </ul>\
            </div>\
        </div>""".format(instance.name, instance.owner, instance.slug)
        fn = "nav_" + instance.slug + ".html"
        f = open(os.path.join(repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        b = repo.create_blob_fromworkdir(fn)
        # bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode )
        bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        bld.write()
        repo.index.read()
        repo.index.add(fn)
        repo.index.write()

        # index.html
        data = """
        <h1>{0}</h1>
        <p><img src="./img/{1}.png"></p>
        <p>Index.html</p>
        """.format(instance.name, instance.slug)
        fn = "index.html"
        f = open(os.path.join(repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        b = repo.create_blob_fromworkdir(fn)
        # bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode )
        bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        bld.write()
        repo.index.read()
        repo.index.add(fn)
        repo.index.write()

        # origin.html
        data = """
        <h1>Origins</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Origins.html</p>
        """.format(instance.slug)
        fn = "origins.html"
        f = open(os.path.join(repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        b = repo.create_blob_fromworkdir(fn)
        # bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode )
        bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        bld.write()
        repo.index.read()
        repo.index.add(fn)
        repo.index.write()

        # tutorial.html
        data = """
        <h1>Tutorial</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Tutorial.html</p>
        """.format(instance.slug)
        fn = "tutorial.html"
        f = open(os.path.join(repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        b = repo.create_blob_fromworkdir(fn)
        # bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode )
        bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        bld.write()
        repo.index.read()
        repo.index.add(fn)
        repo.index.write()

        # software.html
        data = """
        <h1>Software</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Software.html</p>
        """.format(instance.slug)
        fn = "software.html"
        f = open(os.path.join(repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        b = repo.create_blob_fromworkdir(fn)
        # bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode )
        bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        bld.write()
        repo.index.read()
        repo.index.add(fn)
        repo.index.write()

        # teaching.html
        data = """
        <h1>Teaching Materials</h1>
        <p><img src="./img/{0}.png"></p>
        <p>Teaching.html</p>
        """.format(instance.slug)
        fn = "teaching.html"
        f = open(os.path.join(repo.workdir, fn), 'w')
        f.write(data)
        f.close()
        b = repo.create_blob_fromworkdir(fn)
        # bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode )
        bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        bld.write()
        repo.index.read()
        repo.index.add(fn)
        repo.index.write()

        # img/repo.png
        with open(os.path.join(settings.STATIC_ROOT, '../img/default_image.png'), 'rb') as f:
            data = f.read()

        fn = "{}.png".format(instance.slug)
        # f = open(os.path.join(repo.workdir, 'img', fn), 'w')
        # f.write(data)
        # f.close()

        if not os.path.exists(os.path.join(instance.get_repo_path(), 'img')):
            try:
                os.makedirs(os.path.dirname(os.path.join(instance.get_repo_path(), 'img', fn)))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:  # noqa: F821
                    raise
        try:
            file = open(os.path.join(instance.get_repo_path(), 'img', fn), 'wb')
        except OSError:
            pass
        # with open(fn, 'wb') as f:
        #     f.write(data)
        file.write(data)
        file.close()

        b = repo.create_blob_fromworkdir(os.path.join('img', fn))
        bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(instance.get_repo_path(), 'img', fn)).st_mode)
        bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        # bld.write()
        # b = repo.create_blob_fromworkdir(fn)
        # bld = repo.TreeBuilder()
        # bld.insert(fn, b, os.stat(os.path.join(repo.workdir, fn)).st_mode )
        # bld.insert(fn, b, pygit2.GIT_FILEMODE_BLOB)
        bld.write()

        repo.index.read()
        repo.index.add(os.path.join('img', fn))
        repo.index.write()
        tree2 = repo.index.write_tree()

        repo.create_commit('HEAD', s, s, 'Initialized repo\
            with a nav_{}.html, README.html, and pages'.format(instance.slug), tree2, [])


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
