from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import RepositoryModelForm
from .utils import check_repo_name
from .mixins import MultiSlugMixin, OwnerRequiredMix
from repos.models import Repository

import pygit2
from os import path
from shutil import move

from repos.models import Repository

class IndexView(LoginRequiredMixin, ListView):
	model = Repository
	template_name = 'index.html'

	def get_queryset(self):
		queryset = Repository.objects.filter(owner=self.request.user)
		return queryset

class RepositoryDetailView(MultiSlugMixin, DetailView):
	model = Repository
	template_name = 'repoDetail.html'
	
	def get_context_data(self, **kwargs):
		context = super(RepositoryDetailView, self).get_context_data(**kwargs)
		context['test'] = 'test'
		try:
			git_repo = pygit2.Repository(path.join(REPO_DIR, self.kwargs['slug']))
			'''
			git_repo.is_empty()
			'''
			try:
				head = git_repo.revparse_single('HEAD')
			except:
				context['empty'] = True
				return context
			
			tree = head.tree
			ordered_tree = []
			tree_len = 0
			check_readme = 0
			for tr in tree:
				if tr.name == "README.md":
					check_readme = True
				if tr.type == 'tree':
					ordered_tree.insert(tree_len, tr)
					tree_len += 1
				else:
					ordered_tree.append(tr)

			context["tree"] = ordered_tree
			if check_readme:
				readme = tree['README.md'].id
				readme = git_repo[readme]
				context["readme"] = readme
			commitSize = 0
			for i in git_repo.walk(git_repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
				commitSize += 1
			context["commitSize"] = commitSize
			return context
		except:
			context['error_message'] = 'Could not open or locate directory'
			return context
			

class RepositoryCreateView(LoginRequiredMixin, CreateView):
	model = Repository
	template_name = 'create.html'
	form_class = RepositoryModelForm
	# success_url is default to model's get_absolute_url.

	# return HttpResponseRedirect(newRepo.get_absolute_url())

	def form_valid(self, form):
		user = self.request.user
		form.instance.owner = user
		return super(RepositoryCreateView, self).form_valid(form)

	
class RepositoryUpdateView(OwnerRequiredMix, MultiSlugMixin, UpdateView):
	model = Repository
	template_name = 'setting.html'
	form_class = RepositoryModelForm

class RepositoryDeleteView(OwnerRequiredMix, MultiSlugMixin, DeleteView):
	model = Repository
	template_name = 'delete.html'
	success_url = reverse_lazy('index')