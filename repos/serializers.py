from rest_framework import serializers
from . import models

class Repository(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'description',
            'slug',
            'timestamp',
            'owner',
            'editors'
        )
        model = models.Repository
