from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from . import models
from .api.permissions import IsOwnerOrReadOnly
from . import serializers


class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = models.Repository.objects.all()
    serializer_class = serializers.Repository
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend,)
    search_fields = ('name', 'description', 'subject', 'grade_level', 'culture',)
    filter_fields = ('name', 'description', 'subject', 'grade_level', 'culture',)

# filter field USAGE
# api/v1/repository/?name=repo1
# api/v1/repository/?grade_level=2

# search filter and ordering filter USAGE
# api/v1/repository/?search=repo&ordering=name
# api/?search=repo&ordering=-owner   # reverse ordering

# Advanced filters use django-filter which supports highly customizable
# field filtering for REST framework.
# http://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend
