from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from . import models
from . import serializers


class TagAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = models.TagAnalytics.objects.all()
    serializer_class = serializers.TagAnalytics
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
