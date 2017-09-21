from django.conf.urls import url

from .views import TagDetailView, TagListView

app_name = "tags"
urlpatterns = [
    url(r'^$', TagListView.as_view(), name='tag_list'),
    url(r'^(?P<slug>[-\w]+)/$', TagDetailView.as_view(), name='detail'),
]
