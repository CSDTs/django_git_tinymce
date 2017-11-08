from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy

from .utils import (
    owner_editor_check,
    find_file_oid_in_tree,
    create_commit_folders,
    delete_commit,
    delete_commit_folders,
    find_file_oid_in_tree_using_index,
)

from django_git.mixins import OwnerRequiredMixin, OwnerOnlyRequiredMixin
from repos.forms import (
    RepositoryModelForm,
    RepositoryUpdateModelForm,
    CKEditorFileEditForm,
    FileCreateForm,
    FileRenameForm,
    FolderCreateForm,
    RepoForkRenameForm,
    AddEditorsForm
)
from repos.models import Repository, ForkedRepository

from pygit2 import GIT_SORT_TOPOLOGICAL

import pygit2
import os
from pathlib import Path
import shutil
import datetime


User = get_user_model()


class IndexView(LoginRequiredMixin, ListView):
    model = Repository
    template_name = 'gituser/index.html'

    def get_queryset(self):

        queryset = Repository.objects.filter(owner=self.request.user)

        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            ).order_by('name')
        return queryset


class IndividualIndexView(LoginRequiredMixin, ListView):
    model = Repository
    template_name = 'gituser/index.html'

    def get_queryset(self):
        owner_name = self.kwargs['username']
        user_specific = User.objects.get(username=owner_name)
        queryset = Repository.objects.filter(owner=user_specific.id)
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            ).order_by('name')
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(IndividualIndexView, self).get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return context

    def edited_repos(self):
        owner_name = self.kwargs['username']
        user_specific = User.objects.get(username=owner_name)
        return Repository.objects.filter(editors__id=user_specific.id)


class RepositoryListView(LoginRequiredMixin, ListView):
    model = Repository
    template_name = 'gituser/index.html'

    def get_queryset(self):
        queryset = Repository.objects.filter(owner=self.request.user)
        return queryset


class RepositoryCreateView(LoginRequiredMixin, CreateView):
    model = Repository
    template_name = 'repo/create.html'
    form_class = RepositoryModelForm
    # success_url is default to model's get_absolute_url.

    def get_form_kwargs(self):
        kwargs = super(RepositoryCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user

        valid_data = super(RepositoryCreateView, self).form_valid(form)

        return valid_data


class RepositoryDetailView(DetailView):
    model = Repository
    template_name = 'repo/repo_detail.html'

    def get_queryset(self):
        queryset = super(RepositoryDetailView, self).get_queryset()

        return queryset.filter(owner__username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super(RepositoryDetailView, self).get_context_data(**kwargs)

        repo_obj = self.get_object()
        user = self.request.user

        # open repo dir and display repo files
        try:
            git_repo = pygit2.Repository(repo_obj.get_repo_path())

            context['is_owner'] = True if repo_obj.owner == user else False

            if git_repo.is_empty:
                context['empty'] = True

                return context
            else:
                # get last commit
                commit = git_repo.revparse_single('HEAD')
                tree = commit.tree
                tree = sorted(tree, key=lambda entry: entry.filemode)

                context['tree'] = tree
                context['branches'] = list(git_repo.branches)
                context['last_commit'] = commit
                context['branch_name'] = "master"
                context['tab'] = "files"

        except IOError:
            raise Http404("Repository does not exist")

        return context


class ReduxRepositoryDetailView(TemplateView):
    template_name = 'repo/redux_repo.html'
    component = 'repo/src/client.min.js'

    def get_context_data(self, **kwargs):
        context = super(ReduxRepositoryDetailView, self).get_context_data(**kwargs)

        # gets passed to react via window.props
        owner_name = self.kwargs['username']
        repo_name = self.kwargs['slug']
        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs['directories']
        user = User.objects.get(username=owner_name)

        repo = get_object_or_404(Repository, owner=user.id, slug=repo_name)
        forked_repos = ForkedRepository.objects.filter(original=repo)
        fork_count = len(forked_repos)
        try:
            orig_fork = ForkedRepository.objects.get(fork__id=repo.id)
            if orig_fork:
                is_fork = True
            orig = orig_fork.original
            fork_name = orig.slug
            fork_owner = orig.owner.username
        except:
            orig_fork = None
            is_fork = False
            orig = None
            fork_name = None
            fork_owner = None

        props = {
            'repo_name': repo_name,
            'repo_owner': owner_name,
            'repo_owner_id': user.id,
            'repo_id': repo.id,
            'directory': directory,
            'fork_count': fork_count,
            'is_fork': is_fork,
            'fork_name': fork_name,
            'fork_owner': fork_owner,
        }

        context['component'] = self.component
        context['props'] = props

        return context


class ReduxRepositoryFolderDetailView(TemplateView):
    template_name = 'repo/redux_repo.html'
    component = 'repo/src/client.min.js'

    def get_context_data(self, **kwargs):
        context = super(ReduxRepositoryFolderDetailView, self).get_context_data(**kwargs)

        owner_name = self.kwargs['username']
        repo_name = self.kwargs['slug']
        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs['directories']
        if 'directories_ext' in self.kwargs:
            directory += "/" + self.kwargs['directories_ext']
        user = User.objects.get(username=owner_name)
        repo = get_object_or_404(Repository, owner=user.id, slug=repo_name)
        forked_repos = ForkedRepository.objects.filter(original=repo)
        fork_count = len(forked_repos)
        try:
            orig_fork = ForkedRepository.objects.get(fork__id=repo.id)
            if orig_fork:
                is_fork = True
            orig = orig_fork.original
            fork_name = orig.name
            fork_owner = orig.owner.username
        except:
            orig_fork = None
            is_fork = False
            orig = None
            fork_name = None
            fork_owner = None

        props = {
            'repo_name': repo_name,
            'repo_owner': owner_name,
            'repo_owner_id': user.id,
            'repo_id': repo.id,
            'directory': directory,
            'fork_count': fork_count,
            'is_fork': is_fork,
            'fork_name': fork_name,
            'fork_owner': fork_owner,
        }

        context['component'] = self.component
        context['props'] = props

        return context


# Fork Already Named Fork
class RepositoryForkView(LoginRequiredMixin, FormView):
    template_name = 'repo/rename_forked_repo.html'
    form_class = RepoForkRenameForm

    def get_form_kwargs(self):
        kwargs = super(RepositoryForkView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        super(RepositoryForkView, self).form_valid(form)

        User = get_user_model()
        username_in_url = self.kwargs.get("username")
        origin_user = User.objects.get(username=username_in_url)
        new_reponame = form.cleaned_data.get("new_reponame")
        origin_repo = self.kwargs.get("slug")
        origin_repo = get_object_or_404(Repository, slug=origin_repo, owner=origin_user)
        obj = Repository.objects.create(
            name=new_reponame,
            description=origin_repo.description,
            owner=self.request.user
        )
        src = origin_repo.get_repo_path()
        dst = obj.get_repo_path()
        try:
            # if path already exists, remove it before copying with copytree()
            if os.path.exists(dst):
                shutil.rmtree(dst)
                shutil.copytree(src, dst)
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:  # noqa: F821
                shutil.copy(src, dst)
            else:
                print('Directory not copied. Error: %s' % e)

        new_entry = ForkedRepository(original=origin_repo, fork=obj)
        new_entry.save()

        return HttpResponseRedirect(reverse(
            'gitusers:repo_detail',
            args=(self.request.user.username, obj.slug))
        )

    def get_context_data(self, **kwargs):
        context = super(RepositoryForkView, self).get_context_data(**kwargs)

        username_in_url = self.kwargs.get("username")
        # prevents forking your own repo:
        if username_in_url == self.request.user.username:
            raise Http404("You cannot fork your own repo")

        origin_user = User.objects.get(username=username_in_url)
        origin_repo = self.kwargs.get("slug")
        origin_repo = get_object_or_404(Repository, slug=origin_repo, owner=origin_user)

        if Repository.objects.filter(
                slug=origin_repo.slug, owner=self.request.user
        ).exists():
                context['message'] = "You already have a repo with the same name.\
                                        Please rename your fork:"

        return context

    def get_success_url(self):
        return reverse(
            "gitusers:repo_detail",
            kwargs={
                'username': self.request.user.username,
                'slug': self.kwargs.get('slug')
            }
        )


class RepositoryUpdateView(OwnerRequiredMixin, UpdateView):
    model = Repository
    template_name = 'repo/setting.html'
    form_class = RepositoryUpdateModelForm
    id = None

    def editors(self):
        username = self.kwargs.get('username')
        slug = self.kwargs.get('slug')
        repo = get_object_or_404(Repository, owner__username=username, slug=slug)
        editors = repo.editors.all()
        list_to_return = []
        for editor in editors:
            add = User.objects.get(username=editor.username)
            list_to_return.append(add.username)
        return list_to_return

    def get_queryset(self):
        queryset = super(RepositoryUpdateView, self).get_queryset()
        queryset = queryset.filter(owner__username=self.kwargs.get('username'), slug=self.kwargs.get('slug'))
        return queryset

    def get_form_kwargs(self):
        kwargs = super(RepositoryUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'old_name': self.object.name})
        return kwargs

    def form_valid(self, form):
        super(RepositoryUpdateView, self).form_valid(form)

        # de-associate all associated tags and re-create them
        # so that we don't have to go through and compare with get_initial()
        # all again.
        obj = self.get_object()
        form.save()
        slug = slugify(form.cleaned_data.get("name"))
        obj.slug = slug

        obj.save()

        return HttpResponseRedirect(reverse(
            "gitusers:repo_detail",
            kwargs={
                'username': self.kwargs.get('username'),
                'slug': slug
            }
        )
        )


class RepositoryDeleteView(OwnerOnlyRequiredMixin, DeleteView):
    model = Repository
    template_name = 'repo/delete.html'

    def get_queryset(self):
        queryset = super(RepositoryDeleteView, self).get_queryset()

        return queryset.filter(owner__username=self.kwargs.get('username'))

    def get_success_url(self):
        return reverse_lazy('index')

# TODO: Use
#          Tree.__getitem__(name)
#          Tree.__contains__(name)
#       to retrieve and check file.


class RepositoryCreateFileView(OwnerRequiredMixin, FormView):
    template_name = 'repo/create_file.html'
    form_class = FileCreateForm
    repo_obj = None

    def get_initial(self, **kwargs):
        initial = super(RepositoryCreateFileView, self).get_initial()

        self.repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs['username'],
            slug=self.kwargs['slug']
        )

        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs['directories']
        if 'directories_ext' in self.kwargs:
            directory += "/" + self.kwargs['directories_ext']
        if directory != "":
            initial['filename'] = directory + '/.html'
        else:
            initial['filename'] = '.html'
        return initial

    def form_valid(self, form):
        repo = self.repo_obj
        git_repo = pygit2.Repository(repo.get_repo_path())

        filename = form.cleaned_data['filename']
        filecontent = form.cleaned_data['content']
        commit_message = form.cleaned_data['commit_message']

        if not git_repo.is_empty:
            commit = git_repo.revparse_single('HEAD')
            tree = commit.tree

            if find_file_oid_in_tree(filename, tree) != 404:
                form.add_error('filename', "File named {} already exists".format(filename))
                return self.form_invalid(form)

        if ".." in filename:
            form.add_error('filename', "Can't have '..' anywhere in directories structure")
            return self.form_invalid(form)

        dirname = ""
        filename2 = filename
        if "/" in filename:
            dirname, filename2 = os.path.split(filename)

        if not os.path.exists(os.path.join(repo.get_repo_path(), dirname)):
            try:
                os.makedirs(os.path.dirname(os.path.join(repo.get_repo_path(), dirname, filename2)))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:  # noqa: F821
                    raise
        try:
            file = open(os.path.join(repo.get_repo_path(), dirname, filename2), 'w')
        except OSError:
            form.add_error('filename',
                           "Can't add just a directory, must add a file too.\
                           \nExample: foldername/filename.html")
            return self.form_invalid(form)
        file.write(filecontent)
        file.close()
        # b = git_repo.create_blob_fromworkdir(os.path.join(dirname, filename2))
        # bld = git_repo.TreeBuilder()
        # bld.insert(filename2, b, os.stat(os.path.join(repo.get_repo_path(), dirname, filename2)).st_mode)
        # bld.write()
        create_commit_folders(self.request.user, git_repo, commit_message, filename2, dirname)

        return super(RepositoryCreateFileView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RepositoryCreateFileView, self).get_context_data(**kwargs)

        user = self.request.user
        owner = False
        if user.is_superuser:
            owner = True
        if self.repo_obj.owner == user:
            owner = True

        else:
            for editor in self.repo_obj.editors.all():
                if editor.id == user.id:
                    owner = True

        if not owner:
            raise PermissionDenied

        return context

    def get_success_url(self):
        if 'directories_ext' in self.kwargs:
            return reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories'),
                    'directories_ext': self.kwargs.get('directories_ext')
                }
            )
        if 'directories' in self.kwargs:
            return reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories')
                }
            )
        return reverse(
            "gitusers:repo_detail",
            kwargs={
                'username': self.kwargs.get('username'),
                'slug': self.kwargs.get('slug')
            }
        )


class RepositoryCreateFolderView(OwnerRequiredMixin, FormView):
    template_name = 'repo/create_folder.html'
    form_class = FolderCreateForm
    repo_obj = None
    git_repo = None
    folder = None

    def get_form_kwargs(self):
        kwargs = super(RepositoryCreateFolderView, self).get_form_kwargs()

        self.repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs['username'],
            slug=self.kwargs['slug']
        )

        self.git_repo = pygit2.Repository(self.repo_obj.get_repo_path())

        if self.git_repo.is_empty:
            kwargs.update({'tree': None})
            return kwargs

        commit = self.git_repo.revparse_single('HEAD')
        tree = commit.tree
        kwargs.update({'tree': tree})

        return kwargs

    def form_valid(self, form):
        git_repo = pygit2.Repository(self.repo_obj.get_repo_path())

        filename = '.placeholder'
        if "/" not in filename:
            url_directories = ""
            if 'directories' in self.kwargs:
                url_directories += self.kwargs['directories']
            if 'directories_ext' in self.kwargs:
                url_directories += "/" + self.kwargs['directories_ext']
            folder_name = form.cleaned_data['folder_name']
            self.folder = folder_name
            if url_directories == "":
                filename = folder_name + "/" + filename
            else:
                filename = url_directories + "/" + folder_name + "/" + filename
        filecontent = ""
        commit_message = form.cleaned_data['commit_message']

        if not git_repo.is_empty:
            commit = git_repo.revparse_single('HEAD')
            tree = commit.tree

            if find_file_oid_in_tree(filename, tree) != 404:
                form.add_error(None, "File named {} already exists".format(filename))
                return self.form_invalid(form)

        if ".." in filename:
            form.add_error(None, "Can't have '..' anywhere in directories structure")
            return self.form_invalid(form)

        dirname = ""
        filename2 = filename
        if "/" in filename:
            dirname, filename2 = os.path.split(filename)
        if not os.path.exists(os.path.join(self.repo_obj.get_repo_path(), dirname)):
            try:
                os.makedirs(os.path.dirname(os.path.join(self.repo_obj.get_repo_path(), dirname, filename2)))
            except OSError:  # Guard against race condition
                raise
        else:
            if len(os.listdir(self.repo_obj.get_repo_path() + "/" + dirname)) > 0:
                form.add_error(None, "path already exists")
                return self.form_invalid(form)

        try:
            file = open(os.path.join(self.repo_obj.get_repo_path(), dirname, filename2), 'w')
        except OSError:
            form.add_error(None,
                           "Can't add just a directory, must add a file too.\
                           \nExample: foldername/filename.html")
            return self.form_invalid(form)
        file.write(filecontent)
        file.close()
        create_commit_folders(self.request.user, git_repo, commit_message, filename2, dirname)

        return super(RepositoryCreateFolderView, self).form_valid(form)

    def get_success_url(self):
        if 'directories_ext' in self.kwargs:
            return reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories'),
                    'directories_ext': self.kwargs.get('directories_ext') + "/" + self.folder
                }
            )
        if 'directories' in self.kwargs:
            return reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories'),
                    'directories_ext': self.folder
                }
            )
        return reverse(
            "gitusers:repo_detail",
            kwargs={
                'username': self.kwargs.get('username'),
                'slug': self.kwargs.get('slug'),
            }
        )


class BlobEditView(FormView):
    template_name = 'repo/file_edit.html'
    form_class = CKEditorFileEditForm
    blob = None
    repo = None
    repo_obj = None

    def get_initial(self, **kwargs):
        initial = super(BlobEditView, self).get_initial()
        filename = self.kwargs.get('filename')
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')

        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs.get('directories')
        if 'directories_ext' in self.kwargs:
            directory += "/" + self.kwargs.get('directories_ext')

        self.repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs['username'],
            slug=self.kwargs['slug']
        )

        try:
            self.repo = pygit2.Repository(self.repo_obj.get_repo_path())
            if self.repo.is_empty:
                raise Http404
            index_tree = self.repo.index
            commit = self.repo.revparse_single('HEAD')
            tree = commit.tree
            if directory != "":

                folders = directory.split("/")
                dir = ""
                for folder in folders:
                    dir += folder + "/"
                    item = tree.__getitem__(str(dir))
                    index_tree.read_tree(item.id)

            blob_id = find_file_oid_in_tree_using_index(filename, index_tree)
            blob = self.repo[blob_id]

            if not blob.is_binary and isinstance(blob, pygit2.Blob):
                initial['content'] = blob.data

        except IOError:
            raise Http404("Repository does not exist")
        return initial

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        filename = self.kwargs.get('filename')
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')
        directory = ""
        if self.kwargs.get('directories'):
            directory = self.kwargs.get('directories')
        if self.kwargs.get('directories_ext'):
            directory += "/" + self.kwargs.get('directories_ext')

        user = self.request.user

        try:
            repo_path = self.repo_obj.get_repo_path()
            file = open(os.path.join(repo_path, directory, filename), 'w')

            file.truncate()
            file.write(form.cleaned_data['content'])

            file.close()

            commit_message = form.cleaned_data['commit_message']
            commit_message = str(filename) + ' ' + commit_message
            # sha = create_commit(user, self.repo, commit_message, filename)
            create_commit_folders(user, self.repo, commit_message, filename, directory)

        except OSError:
            raise form.ValidationError("Save error, please check the file.")

        return super(BlobEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BlobEditView, self).get_context_data(**kwargs)

        user = self.request.user
        owner = False
        if user.is_superuser:
            owner = True
        if self.repo_obj.owner == user:
            owner = True
        else:
            for editor in self.repo_obj.editors.all():
                if editor.id == user.id:
                    owner = True
        if not owner:
            raise PermissionDenied

        return context

    def get_success_url(self):
        if self.kwargs.get('directories_ext'):
            return reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories'),
                    'directories_ext': self.kwargs.get('directories_ext'),
                }
            )
        elif self.kwargs.get('directories'):
            return reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories'),
                }
            )
        else:
            return reverse(
                "gitusers:repo_detail",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                }
            )


class BlobRawView(View):
    def get(self, request, **kwargs):

        filename = self.kwargs.get('filename')
        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs.get('directories')
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')
        if 'directories_ext' in self.kwargs:
            directory += "/" + self.kwargs.get('directories_ext')
        repo_obj = None

        repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs.get('username'),
            slug=self.kwargs['slug']
        )
        repo = pygit2.Repository(repo_obj.get_repo_path())

        if repo.is_empty:
            raise Http404("File does not exist")

        try:
            index_tree = repo.index
            blob_id = find_file_oid_in_tree_using_index(filename, index_tree)
            if blob_id != 404:
                extension = self.kwargs.get('extension')
                if extension is None:
                    return HttpResponse(repo[blob_id].data)
                if extension in ('.png', '.jpeg', '.jpg', '.gif', '.svg'):
                    return HttpResponse(repo[blob_id].data, content_type="image/png")
                elif extension in ('.pdf'):
                    return HttpResponse(repo[blob_id].data, content_type="application/pdf")
                elif extension in ('.ppt'):
                    return HttpResponse(repo[blob_id].data, content_type="application/vnd.ms-powerpoint")
                elif extension in ('.pptx'):
                    return HttpResponse(
                            repo[blob_id].data,
                            content_type="application/vnd.openxmlformats-\
                            officedocument.presentationml.presentation"
                    )
                elif extension in ('.doc'):
                    return HttpResponse(repo[blob_id].data, content_type="application/msword")
                elif extension in ('.docx'):
                    return HttpResponse(
                            repo[blob_id].data,
                            content_type="application/vnd.openxmlformats-\
                            officedocument.wordprocessingml.document"
                    )
                elif extension in ('.zip'):
                    return HttpResponse(repo[blob_id].data, content_type="application/zip")
                elif extension in ('.rar'):
                    return HttpResponse(repo[blob_id].data, content_type="application/x-rar-compressed")
                elif extension in ('.avi'):
                    return HttpResponse(repo[blob_id].data, content_type="video/x-msvideo")
                elif extension in ('.aac'):
                    return HttpResponse(repo[blob_id].data, content_type="audio/aac")
                elif extension in ('.mpeg'):
                    return HttpResponse(repo[blob_id].data, content_type="video/mpeg")
                elif extension in ('.wav'):
                    return HttpResponse(repo[blob_id].data, content_type="audio/x-wav")
                elif extension in ('.mp3'):
                    return HttpResponse(repo[blob_id].data, content_type="audio/mp3")
                elif extension in ('.mp4'):
                    return HttpResponse(repo[blob_id].data, content_type="video/mp4")
                else:
                    return HttpResponse(repo[blob_id].data)
            else:
                raise Http404("Read raw data error")

        except OSError:
            raise Http404("Failed to open or read file")


class BlobDeleteView(TemplateView):
    template_name = 'repo/delete.html'

    def post(self, request, *args, **kwargs):
        user = self.request.user
        filename = self.kwargs.get("filename")
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')

        repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs.get('username'),
            slug=self.kwargs['slug']
        )

        if not owner_editor_check(repo_obj, user):
            raise PermissionDenied

        try:
            repo = pygit2.Repository(repo_obj.get_repo_path())

            if repo.is_empty:
                raise Http404("File does not exist")
        except:
            raise Http404("Failed to open repository")

        commit_message = filename + ' deleted'
        delete_commit(user, repo, commit_message, filename)

        try:
            os.remove(os.path.join(repo.workdir) + filename)
        except OSError:
            raise Http404("Failed to delete file")

        return HttpResponseRedirect(reverse(
            'gitusers:repo_detail',
            args=(self.kwargs.get('username'), repo_obj.slug))
        )

    def get_context_data(self, *args, **kwargs):
        context = super(BlobDeleteView, self).get_context_data(**kwargs)

        repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs.get('username'),
            slug=self.kwargs['slug']
        )

        if not owner_editor_check(repo_obj, self.request.user):
            raise PermissionDenied

        filename = self.kwargs.get('filename')
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')

        context['object'] = filename
        return context


class BlobDeleteFolderView(TemplateView):

    template_name = 'repo/delete.html'
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):

        user = self.request.user

        repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs.get('username'),
            slug=self.kwargs['slug']
        )

        if not owner_editor_check(repo_obj, user):
            raise PermissionDenied

        filename = self.kwargs.get('filename')
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')

        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs['directories']
        if 'directories_ext' in self.kwargs:
            directory += "/" + self.kwargs['directories_ext']

        try:
            repo = pygit2.Repository(repo_obj.get_repo_path())

            if repo.is_empty:
                raise Http404("The repository is empty")

        except:
            raise Http404("Failed to open repository")

        index_tree = repo.index
        commit = repo.revparse_single('HEAD')
        tree = commit.tree
        folders = directory.split("/")
        for folder in folders:
            try:
                item = tree.__getitem__(str(folder))
                index_tree.read_tree(item.id)
            except:
                pass
        file_name = str(filename)
        commit_message = str(filename) + ' deleted'
        delete_commit_folders(self.request.user, repo, commit_message, file_name, directory)
        try:
            os.remove(os.path.join(repo.workdir, directory, file_name))
        except OSError:
            pass
        if 'directories_ext' in self.kwargs:
            return HttpResponseRedirect(reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories'),
                    'directories_ext': self.kwargs.get('directories_ext')
                }
            )
            )
        if 'directories' in self.kwargs:
            return HttpResponseRedirect(reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories')
                }
            )
            )
        return HttpResponseRedirect(reverse(
            "gitusers:repo_detail",
            kwargs={
                'username': self.kwargs.get('username'),
                'slug': self.kwargs.get('slug')

            }
        )
        )

    def get_context_data(self, *args, **kwargs):
        context = super(BlobDeleteFolderView, self).get_context_data(**kwargs)

        repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs.get('username'),
            slug=self.kwargs['slug']
        )

        if not owner_editor_check(repo_obj, self.request.user):
            raise PermissionDenied

        filename = self.kwargs.get('filename')
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')

        context['object'] = filename
        return context


class RenameFileView(FormView):
    template_name = 'repo/rename_file.html'
    form_class = FileRenameForm

    def get_initial(self, **kwargs):
        initial = super(RenameFileView, self).get_initial()

        self.repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs.get('username'),
            slug=self.kwargs['slug']
        )

        if not owner_editor_check(self.repo_obj, self.request.user):
            raise PermissionDenied

        filename = self.kwargs.get('filename')
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')
        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs.get('directories')
        if 'directories_ext' in self.kwargs:
            directory += "/" + self.kwargs.get('directories_ext')
        try:
            self.repo = pygit2.Repository(self.repo_obj.get_repo_path())

            if self.repo.is_empty:
                raise Http404("No such file")

            index_tree = self.repo.index
            commit = self.repo.revparse_single('HEAD')
            tree = commit.tree

            if directory != "":
                folders = directory.split("/")
                dir = ""
                for folder in folders:
                    dir += folder + "/"
                    item = tree.__getitem__(str(dir))
                    index_tree.read_tree(item.id)

            blob_id = find_file_oid_in_tree_using_index(filename, index_tree)
            blob = self.repo[blob_id]
            if not blob.is_binary and isinstance(blob, pygit2.Blob):
                initial['content'] = blob.data
                initial['new_filename'] = filename

        except IOError:
            raise Http404("Repository does not exist")
        return initial

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        new_filename = form.cleaned_data['new_filename']
        filename = self.kwargs.get('filename')
        if ".." in new_filename:
            form.add_error('new_filename', "Can't have '..' anywhere in rename")
            return self.form_invalid(form)
        if "/" in new_filename:
            form.add_error('new_filename', "Can't have '/' anywhere in rename")
            return self.form_invalid(form)
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')
        directory = ""
        if self.kwargs.get('directories'):
            directory = self.kwargs.get('directories')
        if self.kwargs.get('directories_ext'):
            directory += "/" + self.kwargs.get('directories_ext')
        user = self.request.user
        repo_path = self.repo_obj.get_repo_path()
        # file = open(os.path.join(repo_path, directory, filename), 'w')
        # os.rename('a.txt', 'b.kml')
        old_file = os.path.join(repo_path, directory, filename)
        new_file = os.path.join(repo_path, directory, new_filename)
        Path(new_file)
        index_tree = self.repo.index
        if find_file_oid_in_tree_using_index(new_filename, index_tree) != 404:
            form.add_error('new_filename', "File named {} already exists".format(new_filename))
            return self.form_invalid(form)
        os.rename(old_file, new_file)
        commit_message = form.cleaned_data['commit_message']
        commit_message = 'Renamed ' + str(filename) + ' to ' + str(new_filename) + ' - ' + commit_message
        delete_commit_folders(user, self.repo, commit_message, filename, directory)
        create_commit_folders(user, self.repo, commit_message, new_filename, directory)

        # except OSError:
        #     raise form.ValidationError("Save error, please check the file.")

        return super(RenameFileView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(RenameFileView, self).get_context_data(**kwargs)

        filename = self.kwargs.get('filename')
        if self.kwargs.get('extension'):
            filename += self.kwargs.get('extension')
        context['object'] = filename
        directory = ""
        if self.kwargs.get('directories'):
            directory = self.kwargs.get('directories')
        if self.kwargs.get('directories_ext'):
            directory += "/" + self.kwargs.get('directories_ext')
        context['directory'] = directory

        return context

    def get_success_url(self):
        if 'directories_ext' in self.kwargs:
            return reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories'),
                    'directories_ext': self.kwargs.get('directories_ext')
                }
            )

        if 'directories' in self.kwargs:
            return reverse(
                "gitusers:repo_detail_folder",
                kwargs={
                    'username': self.kwargs.get('username'),
                    'slug': self.kwargs.get('slug'),
                    'directories': self.kwargs.get('directories')
                }
            )

        return reverse(
            "gitusers:repo_detail",
            kwargs={
                'username': self.kwargs.get('username'),
                'slug': self.kwargs.get('slug')

            }
        )


class ForkedReposView(ListView):
    model = ForkedRepository
    template_name = 'repo/forked_repos.html'

    def get_queryset(self):
        self.owner_name = self.kwargs['username']
        self.repo_name = self.kwargs['slug']
        user = User.objects.get(username=self.owner_name)
        try:
            self.repo = Repository.objects.get(owner=user.id, slug=self.repo_name)
        except:
            raise Http404("Repository does not exist")
        forked_repos = ForkedRepository.objects.filter(original=self.repo)
        return forked_repos

    def get_context_data(self, **kwargs):
        context = super(ForkedReposView, self).get_context_data(**kwargs)
        context['orig_repo'] = self.repo
        return context


class CommitLogView(ListView):
    model = Repository
    template_name = 'repo/commits.html'
    paginate_by = 100
    context_object_name = "commits"

    def get_queryset(self):
        self.owner_name = self.kwargs['username']
        self.repo_name = self.kwargs['slug']
        user = User.objects.get(username=self.owner_name)
        repo = Repository.objects.get(owner=user.id, slug=self.repo_name)
        try:
            git_repo = pygit2.Repository(repo.get_repo_path())
        except IOError:
            raise Http404("Repository does not exist")

        class Commit(object):
            message = ""
            hex = ""
            committer = ""
            commit_time = ""

            def __init__(self, hex, message, committer, commit_time):
                self.message = message
                self.hex = hex
                self.committer = committer
                self.commit_time = commit_time

        commits = []
        for commit in git_repo.walk(git_repo.head.target, GIT_SORT_TOPOLOGICAL):
            time3 = datetime.datetime.fromtimestamp(int(commit.commit_time)).strftime('%m-%d-%Y %H:%M:%S')
            commit_obj = Commit(commit.hex, commit.message, commit.committer.name, time3)
            commits.append(commit_obj)

        return commits

    def get_context_data(self, **kwargs):
        context = super(CommitLogView, self).get_context_data(**kwargs)

        context['orig_repo'] = self.repo_name
        context['orig_author'] = self.owner_name

        return context


# TODO: parse diff format same to output of "git show"
class CommitView(TemplateView):
    template_name = 'repo/commit.html'

    def get_context_data(self, **kwargs):
        context = super(CommitView, self).get_context_data(**kwargs)

        owner_name = self.kwargs['username']
        repo_slug = self.kwargs['slug']
        commit_hex = self.kwargs['commit']
        user = User.objects.get(username=owner_name)

        try:
            repo = Repository.objects.get(owner=user.id, slug=repo_slug)
            context['repo'] = repo
        except:
            raise Http404("Repository does not exist")

        try:
            git_repo = pygit2.Repository(repo.get_repo_path())
        except IOError:
            raise Http404("Repository does not exist")

        try:
            commit = git_repo.revparse_single(commit_hex)
            diff = git_repo.diff(commit.parents[0], commit).patch
            files = []
            for e in commit.tree:
                files.append(e.name)

            context['commit'] = commit
            context['diff'] = diff
            context['files'] = files
        except:
            context['commit'] = None

        return context


class AddEditors(FormView):
    template_name = 'repo/add_editors.html'
    form_class = AddEditorsForm

    def get_initial(self, **kwargs):
        username_in_url = self.kwargs.get("username")
        origin_user = User.objects.get(username=username_in_url)
        origin_repo = self.kwargs.get("slug")
        self.repo_obj = get_object_or_404(Repository, slug=origin_repo, owner=origin_user)

        if not owner_editor_check(self.repo_obj, self.request.user):
            raise PermissionDenied

        return super(AddEditors, self).get_initial(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(AddEditors, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        valid_data = super(AddEditors, self).form_valid(form)
        new_editor_username = form.cleaned_data.get("new_editor_username")
        new_editor_email = form.cleaned_data.get("new_editor_username")

        user_pull = None
        try:
            user_pull = User.objects.get(username=new_editor_username)
        except:
            user_pull = User.objects.get(email=new_editor_email)
        if not user_pull:
            form.add_error(None, "User not found")
            return self.form_invalid(form)

        self.repo_obj.editors.add(user_pull)
        self.repo_obj.save()

        return valid_data

    def get_context_data(self, **kwargs):
        username_in_url = self.kwargs.get("username")
        origin_user = User.objects.get(username=username_in_url)
        origin_repo = self.kwargs.get("slug")

        self.repo_obj = get_object_or_404(Repository, slug=origin_repo, owner=origin_user)
        if not owner_editor_check(self.repo_obj, self.request.user):
            raise PermissionDenied

        return super(AddEditors, self).get_context_data(**kwargs)

    def get_success_url(self):
        return reverse(
            "gitusers:setting",
            kwargs={
                'username': self.kwargs.get("username"),
                'slug': self.kwargs.get('slug')
            }
        )


class EditorDeleteView(TemplateView):
    template_name = 'repo/delete.html'

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        username_in_url = self.kwargs.get("username")
        editor_to_delete = self.kwargs.get("editor")

        # get the repo object
        origin_user = get_object_or_404(User, username=username_in_url)
        repo_obj = get_object_or_404(Repository, slug=slug, owner=origin_user)

        # Permission
        if not owner_editor_check(repo_obj, origin_user):
            raise PermissionDenied

        # remove editor
        repo_obj.editors.remove(User.objects.get(username=editor_to_delete))
        repo_obj.save()

        return HttpResponseRedirect(reverse(
            "gitusers:setting",
            kwargs={
                'username': self.kwargs.get("username"),
                'slug': self.kwargs.get('slug')
            }
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(EditorDeleteView, self).get_context_data(**kwargs)

        repo_obj = get_object_or_404(
            Repository,
            owner__username=self.kwargs.get('username'),
            slug=self.kwargs['slug']
        )

        if not owner_editor_check(repo_obj, self.request.user):
            raise PermissionDenied

        context['object'] = self.kwargs.get('editor')
        return context


class SSIFolderView(TemplateView):
    template_name = 'repo/view_ssi1.html'

    def get_object(self):
        username = self.kwargs.get('username')
        slug = self.kwargs.get('slug')
        user = get_object_or_404(User, username=username)
        obj = get_object_or_404(Repository, owner=user, slug=slug)
        return obj

    def get_context_data(self, **kwargs):
        context = super(SSIFolderView, self).get_context_data(**kwargs)
        # self.template_name = 'repo/view_ssi1.html'
        filename = self.kwargs.get('filename')
        # if self.kwargs.get('extension'):
        #     filename += self.kwargs.get('extension')
        filename += ".html"
        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs.get('directories')
        if 'directories_ext' in self.kwargs:
            directory += "/" + self.kwargs.get('directories_ext')
        repo = self.get_object()
        # git_repo = pygit2.Repository(repo.get_repo_path())
        # commit = git_repo.revparse_single('HEAD')
        # tree = commit.tree
        # try:
        #     tree.__getitem__("nav_" + self.kwargs.get('slug') + ".html")
        #     context['nav'] = str(os.path.join(repo.get_repo_path_media(), "nav_" + self.kwargs.get('slug') + ".html"))
        # except KeyError:
        #     context['nav'] = None
        context['url'] = str(os.path.join(repo.get_repo_path_media(), directory, filename))
        # print("url: ----  ", context['url'])
        return context


class SSIPreviewView(TemplateView):
    template_name = 'repo/preview.html'

    def get_object(self):
        username = self.kwargs.get('username')
        slug = self.kwargs.get('slug')
        user = get_object_or_404(User, username=username)
        obj = get_object_or_404(Repository, owner=user, slug=slug)
        return obj

    def get_context_data(self, **kwargs):
        context = super(SSIPreviewView, self).get_context_data(**kwargs)
        filename = self.kwargs.get('filename')
        # if self.kwargs.get('extension'):
        #     filename += self.kwargs.get('extension')
        filename += ".html"
        directory = ""
        if 'directories' in self.kwargs:
            directory = self.kwargs.get('directories')
        if 'directories_ext' in self.kwargs:
            directory += "/" + self.kwargs.get('directories_ext')
        repo = self.get_object()
        # git_repo = pygit2.Repository(repo.get_repo_path())
        # commit = git_repo.revparse_single('HEAD')
        # tree = commit.tree
        # try:
        #     tree.__getitem__("nav_" + self.kwargs.get('slug') + ".html")
        #     context['nav'] = str(os.path.join(repo.get_repo_path_media(), "nav_" + self.kwargs.get('slug') + ".html"))
        # except KeyError:
        #     context['nav'] = None
        # context['url'] = str(os.path.join(repo.get_repo_path_media(), directory, filename))
        context['url'] = str(os.path.join(repo.get_repo_path(), directory, filename))
        print("**********************", context['url'])
        return context
