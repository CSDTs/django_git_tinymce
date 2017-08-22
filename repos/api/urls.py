from django.conf.urls import url

from .views import (
	RepoListAPIView
)
urlpatterns = [
	url(r'^$', RepoListAPIView.as_view(), name='list'),
]
