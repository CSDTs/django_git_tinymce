from django.conf.urls import url

from .views import (
	IndexView,
	BlobEditView,
	BlobRawView,
	RepositoryCreateView,
	RepositoryCreateFileView,
	RepositoryDetailView,
	RepositoryDeleteView,
	RepositoryForkView,
	RepositoryUpdateView,
)

app_name = "gitusers"
urlpatterns = [
	url(r'^$', IndexView.as_view(), name='index'),
	url(r'^create/$', RepositoryCreateView.as_view(), name='create'),
	url(r'^(?P<slug>[-\w]+)/$', RepositoryDetailView.as_view(), name='repo_detail'),
	url(r'^(?P<slug>[-\w]+)/fork/$', RepositoryForkView.as_view(), name='fork'),
	url(r'^(?P<slug>[-\w]+)/create/$', RepositoryCreateFileView.as_view(), name='create_file'),
	url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/edit/$', BlobEditView.as_view(), name='blob_edit'),
	url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobRawView.as_view(), name='blob_raw'),
	# url(r'^(?P<slug>[-\w]+)/commit/(?P<commit>[-\w]+)', CommitView.as_view(), name='commit'),
	url(r'^(?P<slug>[-\w]+)/delete/$', RepositoryDeleteView.as_view(), name='delete'),
	url(r'^(?P<slug>[-\w]+)/setting/$', RepositoryUpdateView.as_view(), name='setting'),
]
