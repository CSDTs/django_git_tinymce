from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import (
	CreateAPIView,
	DestroyAPIView,
	ListAPIView,
	RetrieveAPIView,
	RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny
from repos.models import Repository
from .mixins import RepoDetailFieldLookupMixin
from .permissions import IsOwnerOrReadOnly
from .serializers import (
	RepositoryCreateUpdateSerializer,
	RepositoryDetailSerializer,
	RepositoryListSerializer,
)


class RepoCreateAPIView(CreateAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryCreateUpdateSerializer
	# Permission is default to IsAuthenticatedOrReadOnly in django.settings
	# permission_classes = [IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class RepoDetailAPIView(RepoDetailFieldLookupMixin, RetrieveAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryDetailSerializer
	permission_classes = [AllowAny]
	lookup_fields = ('owner', 'slug')


class RepoDeleteAPIView(RepoDetailFieldLookupMixin, DestroyAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryDetailSerializer
	lookup_fields = ('owner', 'slug')
	permission_classes = [IsOwnerOrReadOnly]


class RepoListAPIView(ListAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryListSerializer
	permission_classes = [AllowAny]
	filter_backends = [SearchFilter, OrderingFilter]
	search_fields = ['name', 'description']

	# search filter and ordering filter USAGE
	# api/?search=repo&ordering=name
	# api/?search=repo&ordering=-owner   # reverse ordering

	# Advanced filters use django-filter which supports highly customizable
	# field filtering for REST framework.
	# http://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend


class RepoUpdateAPIView(RepoDetailFieldLookupMixin, RetrieveUpdateAPIView):
	queryset = Repository.objects.all()
	serializer_class = RepositoryCreateUpdateSerializer
	lookup_fields = ('owner', 'slug')
	permission_classes = [IsOwnerOrReadOnly]
