from django.conf.urls import url

from .views import (
	IndexView,
	BlobView,
	CommitView,
	EditView,
	RepositoryCreateView,
	RepositoryDetailView, 
	RepositoryDeleteView, 
	RepositoryUpdateView
	)

app_name = "gitusers"
urlpatterns = [
	url(r'^$', IndexView.as_view(), name='index'),
	url(r'^create/$', RepositoryCreateView.as_view(), name='create'),
	url(r'^(?P<slug>[-\w]+)/$', RepositoryDetailView.as_view(), name='repo_detail'),
	url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/edit/$', EditView.as_view(), name='blob_edit'),
	url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobView.as_view(), name='blob'),
	url(r'^(?P<slug>[-\w]+)/commit/(?P<commit>[-\w]+)', CommitView.as_view(), name='commit'),
	url(r'^(?P<slug>[-\w]+)/delete/$', RepositoryDeleteView.as_view(), name='delete'),
	url(r'^(?P<slug>[-\w]+)/setting/$', RepositoryUpdateView.as_view(), name='setting'),
]