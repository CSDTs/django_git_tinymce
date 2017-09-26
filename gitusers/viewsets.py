from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from repos.models import Repository as repo_model
from pygit2 import Repository
import json
import datetime

from . import models
from . import serializers
from os import path
import os
import re


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from pathlib import Path

from .utils import create_commit_folders, delete_commit_folders


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
        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs['directories']
        dir_path = path.join(specific_repo.get_repo_path(), directory)
        os.chdir(dir_path)

        index_tree = this_repo.index
        tuplet = []
        time2 = None
        user = request.user
        is_owner = False
        is_editor = False
        if specific_repo.owner == user:
            is_owner = True
        if user.is_superuser:
            is_owner = True
        for editor in specific_repo.editors.all():
            if editor.id == user.id:
                is_editor = True
        empty = False
        if this_repo.is_empty:
            empty = True
        try:
            commit = this_repo.revparse_single('HEAD')
            tree = commit.tree
            folders = []
            if directory != "":
                item = tree.__getitem__(str(directory))
                index_tree.read_tree(item.id)
                for entry in index_tree:
                    name = entry.path
                    filemode = index_tree[entry.path].mode
                    type = ""
                    if filemode is '33188':
                        type = "tree"
                        if name in folders:
                            continue
                        folders.append(name)
                    else:
                        type = "blob"
                    if "/" in entry.path:
                        name = entry.path.split("/")[0]
                        filemode = '100644'
                        type = "tree"
                        if name in folders:
                            continue
                        folders.append(name)

                    tuplet.append({'name': name, 'id': entry.hex, 'type': type, 'filemode': filemode})
            else:
                for entry in tree:
                    tuplet.append(
                        {'name': entry.name,
                         'id': entry.id.hex,
                         'type': entry.type,
                         'filemode': entry.filemode})
            date_handler = lambda obj: (  # noqa: E731
                obj.isoformat()
                if isinstance(obj, (datetime.datetime, datetime.date))
                else None
            )
            time2 = json.dumps(datetime.datetime.fromtimestamp(commit.commit_time), default=date_handler)
            dir_hier = directory

            main_list = {
                        'files': tuplet,
                        'hex': commit.hex,
                        'message': commit.message,
                        'author': commit.author.name,
                        'committer': commit.committer.name,
                        'time': time2,
                        'branches': list(this_repo.branches),
                        'is_owner': is_owner,
                        'is_empty': empty,
                        'dir_hier': dir_hier,
                        'is_editor': is_editor,
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
                        'is_empty': empty,
                        'is_editor': is_editor,
                        'dir_hier': None,
            }

        return Response(main_list, status=status.HTTP_200_OK)

    def post(self, request, format=None, *args, **kw):
        repo = self.kwargs['resource_id']
        directory = ""
        if 'directories' in self.kwargs:
            directory += self.kwargs['directories']
        try:
            specific_repo = repo_model.objects.get(id=repo)
        except:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        this_repo = Repository(specific_repo.get_repo_path())
        for data in request.data.getlist('name'):
            data_name = str(data)
            if '..' in data_name:
                consequitivedots = re.compile(r'\.{2,}')
                data_name = consequitivedots.sub('', data_name)
            file = Path(os.path.join(specific_repo.get_repo_path(), directory, data_name))
            if file.is_file():
                os.remove(os.path.join(specific_repo.get_repo_path(), directory, data_name))
                commit_message = "Clobbered " + data_name + " via upload of same file name to directory"
                delete_commit_folders(self.request.user, this_repo, commit_message, data_name, directory)
            path = default_storage.save(os.path.join(
                specific_repo.get_repo_path(), directory, data_name), ContentFile(data.read()))
            # tmp_file = os.path.join(specific_repo.get_repo_path(), path)
            print('path', path)
            # b = this_repo.create_blob_fromworkdir(os.path.join(directory, data_name))
            # bld = this_repo.TreeBuilder()
            # bld.insert(data_name, b, os.stat(os.path.join(
            #     specific_repo.get_repo_path(), directory, data_name)).st_mode)
            # bld.write()
            commit_message = "Uploaded file " + data_name

            create_commit_folders(self.request.user, this_repo, commit_message, data_name, directory)
        return HttpResponseRedirect(reverse('gitusers:repo_detail', args=(request.user.username, specific_repo.slug)))
