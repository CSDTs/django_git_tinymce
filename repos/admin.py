from django.contrib import admin

# Register models
from .models import Repository

admin.site.register(Repository)