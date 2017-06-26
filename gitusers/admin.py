from django.contrib import admin

# Register your models here
from .models import Owner

# class TagAdmin(admin.ModelAdmin):
#     list_display = ['name', 'description', 'timestamp']
#     list_filter = ['timestamp']
#     search_fields = ['title', 'products']
#     class Meta:
#         model = Repository


admin.site.register(Owner)