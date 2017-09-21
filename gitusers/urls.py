from django.conf.urls import url

from .views import (
    BlobEditView,
    BlobRawView,
    RepositoryCreateView,
    RepositoryCreateFileView,
    # RepositoryDetailView,
    RepositoryDeleteView,
    RepositoryForkView,
    RepositoryUpdateView,
    ReduxRepositoryDetailView,
    ReduxRepositoryFolderDetailView,
    BlobDeleteView,
    BlobDeleteFolderView,
    RenameFileView,
    ForkedReposView,
    IndividualIndexView,
    CommitLogView,
    CommitView,
    AddEditors,
    EditorDeleteView,
)

app_name = "gitusers"
urlpatterns = [
    url(r'^$', IndividualIndexView.as_view(), name='index'),
    url(r'^create/$', RepositoryCreateView.as_view(), name='create'),
    url(r'^(?P<slug>[-\w]+)/$', ReduxRepositoryDetailView.as_view(), name='repo_detail'),

    url(r'^(?P<slug>[-\w]+)/fork/$', RepositoryForkView.as_view(), name='fork'),
    url(r'^(?P<slug>[-\w]+)/forked/$', ForkedReposView.as_view(), name='forked'),
    url(r'^(?P<slug>[-\w]+)/setting/$', RepositoryUpdateView.as_view(), name='setting'),
    url(r'^(?P<slug>[-\w]+)/commit/(?P<commit>[-\w]+)', CommitView.as_view(), name='commit'),
    url(r'^(?P<slug>[-\w]+)/commit/', CommitLogView.as_view(), name='commits'),
    url(r'^(?P<slug>[-\w]+)/addeditor/$', AddEditors.as_view(), name='add_editor'),
    url(r'^(?P<slug>[-\w]+)/deleteeditor/(?P<editor>[-\w]+)/$', EditorDeleteView.as_view(), name='remove_editor'),

    url(r'^(?P<slug>[-\w]+)/(?P<directories_ext>.*)/setting/$', RepositoryUpdateView.as_view(), name='setting'),

    url(r'^(?P<slug>[-\w]+)/delete/$', RepositoryDeleteView.as_view(), name='delete'),

    url(r'^(?P<slug>[-\w]+)/create/$', RepositoryCreateFileView.as_view(), name='create_file'),




    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/create/$', RepositoryCreateFileView.as_view(), name='create_file_dir'),  # noqa: E501
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/create/$', RepositoryCreateFileView.as_view(), name='create_file_folder'),  # noqa: E501


    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/$', ReduxRepositoryFolderDetailView.as_view(), name='repo_detail_folder'),  # noqa: E501






    # blob delete
    url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/delete/$', BlobDeleteView.as_view(), name='blob_delete'),  # noqa: E501
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/delete/$', BlobDeleteFolderView.as_view(), name='blob_delete_dir'),  # noqa: E501
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/delete/$', BlobDeleteFolderView.as_view(), name='blob_delete_folder'),  # noqa: E501


    # Rename file
    url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/rename/$', RenameFileView.as_view(), name='blob_rename'),  # noqa: E501
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/rename/$', RenameFileView.as_view(), name='blob_rename_dir'),  # noqa: E501
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/rename/$', RenameFileView.as_view(), name='blob_rename_folders'),  # noqa: E501




    # Blob raw view
    url(r'^(?P<slug>[-\w]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobRawView.as_view(), name='blob_raw'),
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobRawView.as_view(), name='blob_raw_dir'),  # noqa: E501
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/blob/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobRawView.as_view(), name='blob_raw_folder'),  # noqa: E501

    # blob edit - must be after blob raw view
    url(r'^(?P<slug>[-\w]+)/edit/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobEditView.as_view(), name='blob_edit'),  # noqa: E501
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/edit/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobEditView.as_view(), name='blob_edit_dir'),  # noqa: E501
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/edit/(?P<filename>.*?)(?P<extension>\.[^.]*)?/$', BlobEditView.as_view(), name='blob_edit_folder'),  # noqa: E501



    # testing this out: (need to keep last in list)
    url(r'^(?P<slug>[-\w]+)/(?P<directories>[\w-]+)/(?P<directories_ext>.*)/$', ReduxRepositoryFolderDetailView.as_view(), name='repo_detail_folder'),  # noqa: E501

]
