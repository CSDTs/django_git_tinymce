from django.conf.urls import url

from .views import (
    RepoCreateAPIView,
    RepoDeleteAPIView,
    RepoDetailAPIView,
    RepoListAPIView,
    RepoUpdateAPIView,
)

app_name = "repo_api"
urlpatterns = [
    url(r'^$', RepoListAPIView.as_view(), name='list'),
    url(r'^(?P<owner>[\w.+-]+)/create/$', RepoCreateAPIView.as_view(), name='create'),
    url(r'^(?P<owner>[\w.+-]+)/(?P<slug>[-\w]+)/$', RepoDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<owner>[\w.+-]+)/(?P<slug>[-\w]+)/edit$', RepoUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<owner>[\w.+-]+)/(?P<slug>[-\w]+)/delete$', RepoDeleteAPIView.as_view(), name='delete'),
]
