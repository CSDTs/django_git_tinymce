from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy
from django.shortcuts import render

from analytics.models import TagAnalytics
from django_git.mixins import MultiSlugMixin, OwnerRequiredMix
from django_git.utils import check_repo_name
from repos.forms import RepositoryModelForm, TinyMCEFileEditForm
from repos.models import Repository
from tags.models import Tag

import pygit2
from os import path
from shutil import move


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
				if tag == '' or tag == None:
					continue
				new_tag, created = Tag.objects.get_or_create(title=tag)
				new_tag.repos.add(form.instance)

		return valid_data


class RepositoryDetailView(MultiSlugMixin, DetailView):
	model = Repository
	template_name = 'repo/repo_detail.html'
	#template_name = 'layout_test/repo.html'
	
	def get_context_data(self, **kwargs):
		context = super(RepositoryDetailView, self).get_context_data(**kwargs)
		
		# Increment Tag Analytics
		repo_obj = self.get_object()
		user = self.request.user
		if user.is_authenticated():
			tags = repo_obj.tag_set.all()
			for tag in tags:
				tag_analytics_obj = TagAnalytics.objects.add_count(user, tag)

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
				tree = sorted(tree, key=lambda entry:entry.filemode)

				context['tree'] = tree
				context['branches'] = list(repo_obj.branches)
				context['last_commit'] = commit
				context['branch_name'] = "master"
				context['tab'] = "files"

		except IOError:
			raise Http404("Repository does not exist")

		return context
			

class RepositoryUpdateView(OwnerRequiredMix, MultiSlugMixin, UpdateView):
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
				if tag == '' or tag == None:
					continue
				new_tag, created = Tag.objects.get_or_create(title=tag)
				new_tag.repos.add(self.get_object())
		
		return valid_data

class RepositoryDeleteView(OwnerRequiredMix, MultiSlugMixin, DeleteView):
	model = Repository
	template_name = 'repo/delete.html'
	success_url = reverse_lazy('index')


class CommitView(View):
	pass


class BlobEditView(OwnerRequiredMix, MultiSlugMixin, FormView):
	template_name = 'repo/file_edit.html'
	form_class = TinyMCEFileEditForm
	success_url = '/'
	blob = None

	def get_initial(self, **kwargs):
		initial = super(BlobEditView, self).get_initial()

		filename = self.kwargs.get('filename')
		if self.kwargs.get('extension'):
			filename += self.kwargs.get('extension')
		
		try:
			repo_obj = pygit2.Repository(path.join(settings.REPO_DIR, self.kwargs['slug']))

			if repo_obj.is_empty:
				raise Http404

			commit = repo_obj.revparse_single('HEAD')
			tree = commit.tree
			blob = repo_obj[find_file_oid_in_tree(filename, tree)]

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


		return super(BlobEditView, self).form_valid(form)



def find_file_oid_in_tree(filename, tree):
	for entry in tree:
		if entry.name == filename:
			return entry.id
		else:
			return 404