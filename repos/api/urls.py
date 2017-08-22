from django.conf.urls import url

from .views import (
	RepoDeleteAPIView,
	RepoDetailAPIView,
	RepoListAPIView,
	RepoUpdateAPIView,
)
urlpatterns = [
	url(r'^$', RepoListAPIView.as_view(), name='list'),
	url(r'^(?P<owner>[\w.+-]+)/(?P<slug>[-\w]+)/$', RepoDetailAPIView.as_view(), name='detail'),
	url(r'^(?P<owner>[\w.+-]+)/(?P<slug>[-\w]+)/edit$', RepoUpdateAPIView.as_view(), name='update'),
	url(r'^(?P<owner>[\w.+-]+)/(?P<slug>[-\w]+)/delete$', RepoDeleteAPIView.as_view(), name='delete'),
]
