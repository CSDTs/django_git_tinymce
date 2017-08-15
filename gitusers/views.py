from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
	CreateView,
	UpdateView,
	DeleteView,
	FormView,
)
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy

from .utils import find_file_oid_in_tree, create_commit
from django_git.mixins import OwnerRequiredMixin
from repos.forms import (
	RepositoryModelForm,
	TinyMCEFileEditForm,
	FileCreateForm,
)
from repos.models import Repository
from tags.models import Tag

import pygit2
from os import path
from shutil import copytree


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


# User's repo list view - profile/dashboard
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

		tags = form.cleaned_data.get("tags")
		if tags:
			tags_list = tags.split(',')

			for tag in tags_list:
				tag = str(tag).strip()
				if tag == '' or tag is None:
					continue
				new_tag, created = Tag.objects.get_or_create(title=tag)
				new_tag.repos.add(form.instance)

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


class RepositoryForkView(LoginRequiredMixin, View):
	template = 'repo/fork.html'

	def get(self, request, *args, **kwargs):
		username_in_url = self.kwargs.get("username")
		origin_user = User.objects.get(username=username_in_url)
		origin_repo = self.kwargs.get("slug")
		origin_repo = Repository.objects.get(slug=origin_repo, owner=origin_user)

		context = {}

		try:
			obj = Repository.objects.get(
				slug=origin_repo.name,
				owner=request.user
			)

			context['message'] = "You already have a repo with the same name"

		except Repository.DoesNotExist:
			obj = Repository.objects.create(
				name=origin_repo.name,
				description=origin_repo.description,
				owner=request.user
			)

			copytree(origin_repo.get_repo_path(), obj.get_repo_path())

			return HttpResponseRedirect(reverse(
				'gitusers:repo_detail',
				args=(request.user.username, obj.slug))
			)

		return render(request, self.template, context)


class RepositoryUpdateView(OwnerRequiredMixin, UpdateView):
	model = Repository
	template_name = 'repo/setting.html'
	form_class = RepositoryModelForm

	def get_object(self):
		queryset = super(RepositoryUpdateView, self).get_queryset()
		queryset = queryset.filter(owner__username=self.kwargs.get('username'))
		return queryset.first()

	def get_form_kwargs(self):
		kwargs = super(RepositoryUpdateView, self).get_form_kwargs()
		kwargs.update({'request': self.request})
		return kwargs

	def get_initial(self):
		initial = super(RepositoryUpdateView, self).get_initial()
		tags = self.get_object().tag_set.all()
		initial['tags'] = ", ".join([tag.title for tag in tags])
		return initial

	def form_valid(self, form):
		valid_data = super(RepositoryUpdateView, self).form_valid(form)

		tags = form.cleaned_data.get("tags")
		# de-associate all associated tags and re-create them
		# so that we don't have to go through and compare with get_initial()
		# all again.
		obj = self.get_object()
		obj.tag_set.clear()

		if tags:
			tags_list = tags.split(',')

			for tag in tags_list:
				tag = str(tag).strip()
				if tag == '' or tag is None:
					continue
				new_tag, created = Tag.objects.get_or_create(title=tag)
				new_tag.repos.add(self.get_object())

		return valid_data


class RepositoryDeleteView(OwnerRequiredMixin, DeleteView):
	model = Repository
	template_name = 'repo/delete.html'
	success_url = reverse_lazy('index')

	def get_queryset(self):
		queryset = super(RepositoryDeleteView, self).get_queryset()

		return queryset.filter(owner__username=self.kwargs.get('username'))


class RepositoryCreateFileView(OwnerRequiredMixin, FormView):
	template_name = 'repo/create_file.html'
	form_class = FileCreateForm

	def get_initial(self, **kwargs):
		initial = super(RepositoryCreateFileView, self).get_initial()
		initial['filename'] = '.html'
		return initial

	def form_valid(self, form):
		filename = form.cleaned_data['filename']
		filecontent = form.cleaned_data['content']
		commit_message = form.cleaned_data['commit_message']

		repo = Repository.objects.get(
			owner=self.request.user,
			slug=self.kwargs['slug']
		)
		git_repo = pygit2.Repository(repo.get_repo_path())

		if not git_repo.is_empty:
			commit = git_repo.revparse_single('HEAD')
			tree = commit.tree

			if find_file_oid_in_tree(filename, tree) != 404:
				form.add_error(None, "File named {} already exists".format(filename))
				return self.form_invalid(form)

		file = open(path.join(repo.get_repo_path(), filename), 'w')
		file.write(filecontent)
		file.close()

		create_commit(self.request.user, git_repo, commit_message, filename)

		return super(RepositoryCreateFileView, self).form_valid(form)

	def get_success_url(self):
		return reverse(
			"gitusers:repo_detail",
			kwargs={
				'username': self.request.user.username,
				'slug': self.kwargs.get('slug')
			}
		)


class BlobEditView(OwnerRequiredMixin, FormView):
	template_name = 'repo/file_edit.html'
	form_class = TinyMCEFileEditForm
	blob = None
	repo = None
	repo_obj = None

	def get_initial(self, **kwargs):
		self.success_url = '/{}/{}'.format(self.request.user, self.kwargs['slug'])

		initial = super(BlobEditView, self).get_initial()

		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')

		try:
			self.repo_obj = Repository.objects.get(
				owner=self.request.user,
				slug=self.kwargs['slug']
			)

			self.repo = pygit2.Repository(self.repo_obj.get_repo_path())

			if self.repo.is_empty:
				raise Http404

			commit = self.repo.revparse_single('HEAD')
			tree = commit.tree
			blob = self.repo[find_file_oid_in_tree(filename, tree)]

			if not blob.is_binary and isinstance(blob, pygit2.Blob):
				initial['content'] = blob.data

		except IOError:
			raise Http404("Repository does not exist")
		return initial

	def form_valid(self, form):
		# This method is called when valid form data has been POSTed.
		# It should return an HttpResponse.

		# Base object is immutable and Blob doesn't have a constructor
		# Have to directly change the actually file in file system
		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')

		user = self.request.user

		try:
			repo_path = self.repo_obj.get_repo_path()
			file = open(path.join(repo_path, filename), 'w')

			file.truncate()
			file.write(form.cleaned_data['content'])

			file.close()

			commit_message = form.cleaned_data['commit_message']
			commit_message = str(filename) + ' ' + commit_message
			# sha = create_commit(user, self.repo, commit_message, filename)
			create_commit(user, self.repo, commit_message, filename)

		except OSError:
			raise form.ValidationError("Save error, please check the file.")

		return super(BlobEditView, self).form_valid(form)


class BlobRawView(View):
	def get(self, request, **kwargs):

		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')

		repo_obj = None

		try:
			repo_obj = Repository.objects.get(
				owner__username=self.kwargs.get('username'),
				slug=self.kwargs['slug']
			)
			repo = pygit2.Repository(repo_obj.get_repo_path())

			if repo.is_empty:
				print('asdfasdfasdfasfd')
				raise Http404("The repository is empty")

		except:
			raise Http404("Failed to open repository")

		try:
			commit = repo.revparse_single('HEAD')
			tree = commit.tree
			blob_id = find_file_oid_in_tree(filename, tree)
			if blob_id != 404:
				return HttpResponse(repo[blob_id].data)
			else:
				return Http404("Read raw data error")

		except OSError:
			raise Http404("Failed to open or read file")
