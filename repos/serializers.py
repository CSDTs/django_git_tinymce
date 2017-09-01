from rest_framework import serializers
from . import models


class Repository(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        fields = (
            'id',
            'name',
            'description',
            'slug',
            'timestamp',
            'owner',
            'owner_username',
            'editors'
        )
        model = models.Repository
