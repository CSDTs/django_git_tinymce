from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.views import APIView

from repos.models import Repository as repo_model
from pygit2 import Repository, Signature
from time import time
import json
import datetime


from . import models
from . import serializers


class OwnerViewSet(viewsets.ModelViewSet):
    queryset = models.Owner.objects.all()
    serializer_class = serializers.Owner
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class FilesView(APIView):
    def get(self, request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        repo = self.kwargs['resource_id']
        try:
            specific_repo = repo_model.objects.get(id=repo)
        except:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        this_repo = Repository(specific_repo.get_repo_path())
        tuplet = []
        try:
            commit = this_repo.revparse_single('HEAD')
            tree = commit.tree
        except:
            # no files, no initial commit so no head hex
            return Response(tuplet, status=status.HTTP_200_OK)
        for entry in tree:
            tuplet.append({'name': entry.name, 'id': entry.id.hex, 'type': entry.type, 'filemode': entry.filemode})
        main_list = []
        main_list.append({'files':tuplet})

        third_tuplet = []
        third_tuplet.append({'hex': commit.hex})
        third_tuplet.append({'message': commit.message})
        third_tuplet.append({'author': commit.author.name})
        third_tuplet.append({'committer': commit.committer.name})
        date_handler = lambda obj: (
            obj.isoformat()
            if isinstance(obj, (datetime.datetime, datetime.date))
            else None
        )
        time = json.dumps(datetime.datetime.fromtimestamp(commit.commit_time), default=date_handler)
        third_tuplet.append({'time': time})
        main_list.append({'last_commit': third_tuplet})


        main_list.append({'branches': list(this_repo.branches)})

        user = request.user
        is_owner = True if specific_repo.owner == user else False
        main_list.append({'is_owner': is_owner})
        empty = False
        if this_repo.is_empty:
            empty = True
        main_list.append({'empty':empty})
        final_tuple = tuple(main_list)
        return Response(final_tuple, status=status.HTTP_200_OK)
