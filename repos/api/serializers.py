from rest_framework.serializers import ModelSerializer

from repos.models import Repository


class RepositoryListSerializer(ModelSerializer):
	class Meta:
		model = Repository
		fields = (
			'id',
			'name',
			'description',
			'slug',
			'owner',
		)


class RepositoryDetailSerializer(ModelSerializer):
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

"""

data = {
	'name': 'repo3',
	'owner': 1,
	'slug': 'repo3'
}

obj = Repository.objects.get(id=3)

new_obj = RepositoryDetailSerializer(data=data)
if new_obj.is_valid():
	new_obj.save()
else:
	print(new_obj.errors)
"""