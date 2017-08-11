from rest_framework import serializers
from . import models

class Owner(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'user',
        )
        model = models.Owner
