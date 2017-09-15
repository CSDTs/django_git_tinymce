from django.contrib import admin

# Register your models here
from .models import Repository
from tags.models import Tag


class TagInline(admin.StackedInline):
	model = Tag.repos.through


class RepoAdmin(admin.ModelAdmin):
	list_display = ['dir', 'name', 'description', 'owner', 'timestamp']
	list_display_links = ['dir', 'name']
	list_filter = ['timestamp']
	search_fields = ['name', 'description']
	inlines = [TagInline,]

	class Meta:
		model = Repository

	def dir(self, obj):
		return obj.pk


admin.site.register(Repository, RepoAdmin)
