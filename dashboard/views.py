from django.shortcuts import render
from django.views.generic.list import ListView
#from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from repos.models import Repository

# using generic views -- ListView and DetailView
class IndexView(LoginRequiredMixin, ListView):
	template_name = 'index.html'
	context_object_name = 'repos'

	def get_queryset(self):
		"""
		Return the last five published questions (not including those set to be
		published in the future).
		"""
		# __lte --> less than or equal
		filtered_repos = Repository.objects.all()
		return filtered_repos