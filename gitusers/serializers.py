from django.contrib.auth.models import User
# from rest_framework.response import Response
from rest_framework import serializers

# from pygit2 import Repository

from . import models
# from repos.models import Repository


class Owner(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'user',
        )
        model = models.Owner


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
        lookup_field = 'id'
