import misaka

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Repo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, blank=True, related_name="repo_user")
    name = models.CharField(max_length=255, unique=True, null=False, default='repo-name')
    slug = models.SlugField(allow_unicode=True, unique=True, default='repo-name')
    created_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True)
    description_html = models.TextField(null=True, editable=False)

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.description_html = misaka.html(self.description)
        super().save(*args, **kwargs)

    # def get_absolute_url(self):
    #    return reverse(
    #        "posts:single",
    #        kwargs={
    #            "username": self.user.username,
    #            "pk": self.pk
    #        }
    #    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "slug"]
        verbose_name_plural = "repos"


class Document(models.Model):
    repo = models.ForeignKey(Repo)
    url = models.CharField(max_length=255, null=True, blank=True)


MEMBERSHIP_CHOICES = (
    (0, "banned"),
    (1, "member"),
    (2, "moderator"),
    (3, "admin")
)


class Ownership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="repo_ownership_user")
    repo = models.ForeignKey(Repo, related_name="ownership")
    role = models.IntegerField(choices=MEMBERSHIP_CHOICES, default=1)

    def __str__(self):
        return "{} is {} in {}".format(
            self.user.username,
            self.role,
            self.repo.slug
        )

    class Meta:
        permissions = (
            ("ban_member", "Can ban members"),
        )
        unique_together = ("repo", "user")
