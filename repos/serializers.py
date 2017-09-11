from rest_framework import serializers

import os

from . import models



class Repository(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    photo_url = serializers.SerializerMethodField()

    # provides the link to JSONIfy the image, stored in media
    def get_photo_url(self, Repository):
        request = self.context.get('request')
        if Repository.image:
            link = Repository.image.url
            return request.build_absolute_uri(link)
        else:
            link = os.path.join('/static', 'img', 'default_repo.png')
            return request.build_absolute_uri(link)



    class Meta:
        fields = (
            'id',
            'name',
            'description',
            'slug',
            'timestamp',
            'owner',
            'owner_username',
            'editors',
            'photo_url'
        )
        model = models.Repository
