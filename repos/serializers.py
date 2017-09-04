from rest_framework.serializers import (
    # HyperlinkedIdentityField,
    ModelSerializer,
    ReadOnlyField,
)
from .models import Repository


class Repository(ModelSerializer):
    owner_username = ReadOnlyField(source='owner.username')
    # DETAIL_URL = HyperlinkedIdentityField(view_name='api-repository-detail')

    class Meta:
        fields = (
            # 'DETAIL_URL',
            'id',
            'name',
            'description',
            'slug',
            'timestamp',
            'owner',
            'owner_username',
            'editors'
        )
        model = Repository
