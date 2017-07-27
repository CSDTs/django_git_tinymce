from django.contrib import admin

# Register your models here
from .models import Repository


class RepoAdmin(admin.ModelAdmin):
	list_display = ['name', 'description', 'timestamp']
	list_filter = ['timestamp']
	search_fields = ['name', 'description']

	class Meta:
		model = Repository


admin.site.register(Repository, RepoAdmin)
