from django.contrib import admin

# Register your models here.
from .models import TagAnalytics

class TagAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['tag', 'count']
    class Meta:
        model = TagAnalytics

admin.site.register(TagAnalytics, TagAnalyticsAdmin)