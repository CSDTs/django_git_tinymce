from os import path

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import Repository
from .forms import CreateRepo
from .utils import check_repo_name
from django_git.settings import REPO_DIR

import pygit2

'''
IndexView(generic.ListView)
RepoDerailView(generic.DetailView)

TODO:
- def createRepo
- def deleteRepo
- def view_raw(request)
- create file in a repo: http://www.pygit2.org/objects.html#pygit2.Repository.create_blob
- create folder in a repo: http://www.pygit2.org/objects.html#pygit2.Repository.TreeBuilder

'''
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

def createRepo(request):
	'''
	init the repo on model creation???
	Or wait til some point when need to edit the repo?
	'''
	template_name = 'repos/create.html'
	context = {}
	
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = CreateRepo(request.POST)

		if form.is_valid():
			# process the data in form.cleaned_data as required
			name = form.cleaned_data['repositoryName']
			name = check_repo_name(name)
			desc = form.cleaned_data['repositoryDesc']

			# Check repo existence and create
			newRepo, created = Repository.objects.get_or_create(name=name, description=desc)
			if created:
				newRepo.save()
				# Always return an HttpResponseRedirect after successfully dealing
				# with POST data. This prevents data from being posted twice if a
				# user hits the Back button.
				return HttpResponseRedirect(reverse('repos:detail', args=(name,)))

			else:
				error_message = "Repository name is taken."
				context['error_message'] = error_message
				return render(request, template_name, context)
			
		else:
			context['error_message'] = 'Form invalid'
	else:
		form = CreateRepo()

	context['form'] = form
	return render(request, template_name, context)

'''
def deleteRepo(request):
'''

class TestView(ListView):
	template_name = 'repos/test.html'
	context_object_name = 'repos'

	def get_queryset(self):
		"""
		Return the last five published questions (not including those set to be
		published in the future).
		"""
		# __lte --> less than or equal
		filtered_repos = Repository.objects.all()
		return filtered_repos