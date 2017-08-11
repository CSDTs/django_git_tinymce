from rest_framework import serializers
from . import models

class Tag(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'title',
            'repos',
            'slug',
            'active',
        )
        model = models.Tag
