from rest_framework.generics import (
	DestroyAPIView,
	ListAPIView,
	RetrieveAPIView,
	UpdateAPIView,
)

from repos.models import Repository
from .mixins import RepoDetailFieldLookupMixin
from .serializers import RepositoryListSerializer
from .serializers import RepositoryDetailSerializer

class RepoListAPIView(ListAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryListSerializer


class RepoDetailAPIView(RepoDetailFieldLookupMixin, RetrieveAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryDetailSerializer
	lookup_fields = ('owner', 'slug')


class RepoUpdateAPIView(RepoDetailFieldLookupMixin, UpdateAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryDetailSerializer
	lookup_fields = ('owner', 'slug')


class RepoDeleteAPIView(RepoDetailFieldLookupMixin, DestroyAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryDetailSerializer
	lookup_fields = ('owner', 'slug')