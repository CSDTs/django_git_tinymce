from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
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


class UserView(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    model = User
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = User.objects.all()



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
        time = None
        user = request.user
        is_owner = True if specific_repo.owner == user else False
        empty = False
        if this_repo.is_empty:
            empty = True
        try:
            commit = this_repo.revparse_single('HEAD')
            tree = commit.tree
            for entry in tree:
                tuplet.append({'name': entry.name, 'id': entry.id.hex, 'type': entry.type, 'filemode': entry.filemode})
            date_handler = lambda obj: (
                obj.isoformat()
                if isinstance(obj, (datetime.datetime, datetime.date))
                else None
            )
            time = json.dumps(datetime.datetime.fromtimestamp(commit.commit_time), default=date_handler)

            main_list = {
                        'files': tuplet,
                        'hex': commit.hex,
                        'message': commit.message,
                        'author': commit.author.name,
                        'committer': commit.committer.name,
                        'time': time,
                        'branches': list(this_repo.branches),
                        'is_owner': is_owner,
                        'is_empty': empty
            }

        except:
            # no files, no initial commit so no head hex
            main_list = {
                        'files': tuplet,
                        'hex': None,
                        'message': None,
                        'author': None,
                        'committer': None,
                        'time': None,
                        'branches': [],
                        'is_owner': is_owner,
                        'is_empty': empty
            }

        return Response(main_list, status=status.HTTP_200_OK)
