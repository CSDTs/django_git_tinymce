from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.list import ListView

from repos.models import Repository


class IndexView(LoginRequiredMixin, ListView):
	model = Repository
	template_name = 'gituser/index.html'

	def get_queryset(self):
		queryset = Repository.objects.filter(owner=self.request.user)
		return queryset