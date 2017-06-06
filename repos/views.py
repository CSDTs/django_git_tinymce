from os import path

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q
from django.shortcuts import render

from .models import Repository
from .forms import CreateRepo
from django_git.settings import REPO_DIR

import pygit2

# using generic views -- ListView and DetailView
class IndexView(ListView):
	template_name = 'repos/index.html'
	context_object_name = 'repos'

	def get_queryset(self):
		"""
		Return the last five published questions (not including those set to be
		published in the future).
		"""
		# __lte --> less than or equal
		filtered_repos = Repository.objects.all()
		return filtered_repos

class RepositoryDetailView(DetailView):
	model = Repository
	template_name = 'repos/repoDetail.html'
	
	def get_context_data(self, **kwargs):
		context = super(RepositoryDetailView, self).get_context_data(**kwargs)

		try:
			git_repo = pygit2.Repository(path.join(REPO_DIR, self.kwargs['pk']))
			try:
				head = git_repo.revparse_single('HEAD')
			except:
				context['empty'] = 1
				return context
			
			tree = head.tree
			ordered_tree = []
			tree_len = 0
			check_readme = 0
			for tr in tree:
				if tr.name == "README.md":
					check_readme = 1
				if tr.type == 'tree':
					ordered_tree.insert(tree_len, tr)
					tree_len += 1
				else:
					ordered_tree.append(tr)

			context["tree"] = ordered_tree
			if check_readme == 1:
				readme = tree['README.md'].id
				eadme = git_repo[readme]
				context["readme"] = readme
			commitSize = 0
			for i in git_repo.walk(git_repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
				commitSize += 1
			context["commitSize"] = commitSize
			return context
		except:
			context['error_message'] = 'Could not open or locate directory'


def create(request):
	template_name = 'repos/create.html'
	context = {}

	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = CreateRepo(request.POST)

	if form.is_valid():
		# process the data in form.cleaned_data as required
		name = form.cleaned_data['repositoryName']
		desc = form.cleaned_data['repositoryDesc']

		'''
		TODO: check name existence and create/return error_message
		'''

		# redirect to a new URL:
		return HttpResponseRedirect('/repos/name')


	return render(request, context, template_name)