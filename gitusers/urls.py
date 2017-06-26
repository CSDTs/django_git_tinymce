from django.conf.urls import url

from django_git.views import RepositoryDetailView, RepositoryDeleteView, RepositoryUpdateView
from .views import IndexView

urlpatterns = [
	url(r'^$', IndexView.as_view(), name='index'),
	url(r'^(?P<slug>[-\w]+)/$', RepositoryDetailView.as_view(), name='repo_detail'),
	url(r'^(?P<slug>[-\w]+)/delete/$', RepositoryDeleteView.as_view(), name='delete'),
	url(r'^(?P<slug>[-\w]+)/setting/$', RepositoryUpdateView.as_view(), name='setting'),
]