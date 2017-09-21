from rest_framework.serializers import ModelSerializer

from accounts.api.serializers import UserDetailSerializer
from .serializer_relations import ParameterisedHyperlinkedIdentityField
from repos.models import Repository

DETAIL_URL = ParameterisedHyperlinkedIdentityField(
    view_name='repo_api:detail',
    lookup_fields=(('owner', 'owner'), ('slug', 'slug'),)
)

DELETE_URL = ParameterisedHyperlinkedIdentityField(
    view_name='repo_api:delete',
    lookup_fields=(('owner', 'owner'), ('slug', 'slug'),)
)


class RepositoryCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = Repository
        fields = (
            'name',
            "description",
        )


class RepositoryDetailSerializer(ModelSerializer):
    detail_url = DETAIL_URL
    delete_url = DELETE_URL
    owner = UserDetailSerializer(read_only=True)

    class Meta:
        model = Repository
        fields = (
            'detail_url',
            'id',
            'name',
            'description',
            'slug',
            'timestamp',
            'owner',
            'editors',
            'delete_url',
        )


class RepositoryListSerializer(ModelSerializer):
    detail_url = DETAIL_URL
    delete_url = DELETE_URL
    owner = UserDetailSerializer(read_only=True)

    class Meta:
        model = Repository
        fields = (
            'detail_url',
            'name',
            'description',
            'slug',
            'owner',
            'delete_url',
        )
