from rest_framework.serializers import ModelSerializer

from repos.models import Repository


class RepositorySerializer(ModelSerializer):
	class Meta:
		model = Repository
		fields = (
			'id',
            'name',
            'description',
            'slug',
            'timestamp',
            'owner',
            'editors',
		)