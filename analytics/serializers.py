from rest_framework import serializers
from . import models

class TagAnalytics(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'user',
            'tag',
            'count',
        )
        model = models.TagAnalytics
