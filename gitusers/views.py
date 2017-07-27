from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
	CreateView,
	UpdateView,
	DeleteView,
	FormView
)
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from analytics.models import TagAnalytics
from django_git.mixins import OwnerRequiredMix
from repos.forms import RepositoryModelForm, TinyMCEFileEditForm
from repos.models import Repository
from tags.models import Tag

import pygit2
from os import path
# from shutil import move


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
	# template_name = 'layout_test/repo.html'

	def get_context_data(self, **kwargs):
		context = super(RepositoryDetailView, self).get_context_data(**kwargs)

		# Increment Tag Analytics
		repo_obj = self.get_object()
		user = self.request.user
		if user.is_authenticated():
			tags = repo_obj.tag_set.all()
			for tag in tags:
				# tag_analytics_obj = TagAnalytics.objects.add_count(user, tag)
				TagAnalytics.objects.add_count(user, tag)

		# open repo dir and display repo files
		try:
			repo_obj = pygit2.Repository(path.join(settings.REPO_DIR, self.kwargs['slug']))

			if repo_obj.is_empty:
				context['empty'] = True
				return context
			else:
				# get last commit
				commit = repo_obj.revparse_single('HEAD')
				tree = commit.tree
				tree = sorted(tree, key=lambda entry: entry.filemode)

				context['tree'] = tree
				context['branches'] = list(repo_obj.branches)
				context['last_commit'] = commit
				context['branch_name'] = "master"
				context['tab'] = "files"

		except IOError:
			raise Http404("Repository does not exist")

		return context


class RepositoryUpdateView(OwnerRequiredMix, UpdateView):
	model = Repository
	template_name = 'repo/setting.html'
	form_class = RepositoryModelForm

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


class RepositoryDeleteView(OwnerRequiredMix, DeleteView):
	model = Repository
	template_name = 'repo/delete.html'
	success_url = reverse_lazy('index')


class BlobEditView(OwnerRequiredMix, FormView):
	template_name = 'repo/file_edit.html'
	form_class = TinyMCEFileEditForm
	blob = None
	repo_obj = None

	def get_initial(self, **kwargs):
		self.success_url = '/{}/{}'.format(self.request.user, self.kwargs['slug'])

		initial = super(BlobEditView, self).get_initial()

		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')

		try:
			self.repo_obj = pygit2.Repository(path.join(settings.REPO_DIR, self.kwargs['slug']))

			if self.repo_obj.is_empty:
				raise Http404

			commit = self.repo_obj.revparse_single('HEAD')
			tree = commit.tree
			blob = self.repo_obj[find_file_oid_in_tree(filename, tree)]

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

		try:
			file = open(path.join(settings.REPO_DIR, self.kwargs['slug'], filename), 'w')

			file.truncate()
			file.write(form.cleaned_data['content'])

			file.close()

			user = self.request.user
			commit_message = form.cleaned_data['commit_message']
			# sha = create_commit(user, self.repo_obj, commit_message, filename)
			create_commit(user, self.repo_obj, commit_message, filename)

		except OSError:
			raise form.ValidationError("Save error, please check the file.")

		return super(BlobEditView, self).form_valid(form)


class BlobRawView(View):
	def get(self, request, **kwargs):

		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')

		try:
			self.repo_obj = pygit2.Repository(path.join(settings.REPO_DIR, self.kwargs['slug']))

			if self.repo_obj.is_empty:
				raise Http404("The repository is empty")

		except:
			raise Http404("Failed to open repository")

		try:
			file = open(path.join(settings.REPO_DIR, self.kwargs['slug'], filename), 'r')
			file_raw = file.read()
			file.close()

			return HttpResponse(file_raw)

		except OSError:
			raise Http404("Failed to open or read file")


def find_file_oid_in_tree(filename, tree):
	for entry in tree:
		if entry.name == filename:
			return entry.id
		else:
			return 404


def create_commit(user, repo, message, filename):
	from pygit2 import Signature
	# example:
	'''
	author = Signature('Alice Author', 'alice@authors.tld')
	committer = Signature('Cecil Committer', 'cecil@committers.tld')
	tree = repo.TreeBuilder().write()
	repo.create_commit(
		'refs/heads/master', # the name of the reference to update
		author, committer, 'one line commit message\n\ndetailed commit message',
		tree, # binary string representing the tree object ID
		[] # list of binary strings representing parents of the new commit
	)
	'''
	ref = 'refs/heads/master'
	author = Signature(user.username, user.email)
	committer = Signature(user.username, user.email)
	repo.index.add(filename)
	repo.index.write()
	tree = repo.index.write_tree()
	parent = None
	try:
		parent = repo.revparse_single('HEAD')
	except KeyError:
		pass

	parents = []
	if parent:
		parents.append(parent.oid.hex)

	sha = repo.create_commit(ref, author, committer, message, tree, parents)
	return sha
