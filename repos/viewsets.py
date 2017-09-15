from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
# from rest_framework.permissions import IsAuthenticatedOrReadOnly

from . import models
from .api.permissions import IsOwnerOrReadOnly
from . import serializers


class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = models.Repository.objects.all()
    serializer_class = serializers.Repository
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']

# search filter and ordering filter USAGE
# api/?search=repo&ordering=name
# api/?search=repo&ordering=-owner   # reverse ordering

# Advanced filters use django-filter which supports highly customizable
# field filtering for REST framework.
# http://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend
