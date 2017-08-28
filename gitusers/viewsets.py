from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

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
from os import path
import os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


from .utils import create_commit


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

    def post(self, request, format=None, *args, **kw):
        repo = self.kwargs['resource_id']
        try:
            specific_repo = repo_model.objects.get(id=repo)
        except:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        this_repo = Repository(specific_repo.get_repo_path())
        print(this_repo)

        data = request.data
        print(data)
        data_name = str(data['name'])
        data2 = data['name']
        path = default_storage.save(os.path.join(specific_repo.get_repo_path(), data_name), ContentFile(data2.read()))
        print('path', path)
        tmp_file = os.path.join(specific_repo.get_repo_path(), path)

        b = this_repo.create_blob_fromworkdir(data_name)
        bld = this_repo.TreeBuilder()
        bld.insert(data_name, b, os.stat(os.path.join(specific_repo.get_repo_path(), data_name)).st_mode )
        t = bld.write()
        this_repo.index.read()
        this_repo.index.add(data_name)
        this_repo.index.write()
        email = "nonegiven@nonegiven.com"
        if self.request.user.email:
            email = self.request.user.email
		# s = pygit2.Signature(self.request.user.username, email, int(time()), 0)
		#s = pygit2.Signature('Alice Author', 'alice@authors.tld', int(time()), 0)
		#c = this_repo.create_commit('HEAD', s,s, commit_message, t, [this_repo.head.target])
        commit_message = "Uploaded file"

        create_commit(self.request.user, this_repo, commit_message, data_name)
        return HttpResponseRedirect(reverse(
			'gitusers:repo_detail',
			args=(request.user.username, specific_repo.slug))
        )
