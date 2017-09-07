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
	ReduxRepositoryDetailView,
	ReduxRepositoryFolderDetailView,
	BlobDeleteView,
	BlobDeleteFolderView,
	RenameFileView,
	ForkedReposView,
	IndividualIndexView
)

app_name = "gitusers"
urlpatterns = [
	url(r'^$', IndividualIndexView.as_view(), name='index'),
	url(r'^create/$', RepositoryCreateView.as_view(), name='create'),
	url(r'^(?P<slug>[-\w]+)/$', ReduxRepositoryDetailView.as_view(), name='repo_detail'),

	url(r'^(?P<slug>[-\w]+)/fork/$', RepositoryForkView.as_view(), name='fork'),
	url(r'^(?P<slug>[-\w]+)/forked/$', ForkedReposView.as_view(), name='forked'),
	url(r'^(?P<slug>[-\w]+)/setting/$', RepositoryUpdateView.as_view(), name='setting'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories_ext>.*)/setting/$', RepositoryUpdateView.as_view(), name='setting'),

	url(r'^(?P<slug>[-\w]+)/delete/$', RepositoryDeleteView.as_view(), name='delete'),

	url(r'^(?P<slug>[-\w]+)/create/$', RepositoryCreateFileView.as_view(), name='create_file'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/create/$', RepositoryCreateFileView.as_view(), name='create_file_dir'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/create/$', RepositoryCreateFileView.as_view(), name='create_file_folder'),


	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/$', ReduxRepositoryFolderDetailView.as_view(), name='repo_detail_folder'),


	# blob edit
	url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/edit/$', BlobEditView.as_view(), name='blob_edit'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/edit/$', BlobEditView.as_view(), name='blob_edit_dir'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/edit/$', BlobEditView.as_view(), name='blob_edit_folder'),



	# blob delete
	url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/delete/$', BlobDeleteView.as_view(), name='blob_delete'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/delete/$', BlobDeleteFolderView.as_view(), name='blob_delete_dir'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/delete/$', BlobDeleteFolderView.as_view(), name='blob_delete_folder'),


	# Rename file
	url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/rename/$', RenameFileView.as_view(), name='blob_rename'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/rename/$', RenameFileView.as_view(), name='blob_rename_dir'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/rename/$', RenameFileView.as_view(), name='blob_rename_folders'),




	# Blob raw view
	url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobRawView.as_view(), name='blob_raw'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobRawView.as_view(), name='blob_raw_dir'),
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobRawView.as_view(), name='blob_raw_folder'),

	# url(r'^(?P<slug>[-\w]+)/commit/(?P<commit>[-\w]+)', CommitView.as_view(), name='commit'),


	# testing this out: (need to keep last in list)
	url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/$', ReduxRepositoryFolderDetailView.as_view(), name='repo_detail_folder'),
]
