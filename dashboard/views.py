from django.db.models import Q
from django.views import View
from django.views.generic.list import ListView
from django.shortcuts import render

from analytics.models import TagAnalytics
from repos.models import Repository


class DashboardView(View):
	template = 'dashboard/index.html'

	def get(self, request, *args, **kwargs):
		tag_analytics = None
		repos = None
		top_tags = None

		try:
			if request.user.is_authenticated():
				tag_analytics = request.user.taganalytics_set.all().order_by("-count")
			else:
				tag_analytics = TagAnalytics.objects.all().order_by("-count")
		except:
			pass

		# repos associated to theses tags
		if tag_analytics:
			top_tags = [x.tag for x in tag_analytics]
			repos = Repository.objects.filter(tag__in=top_tags).distinct()

		context = {
			"repos": repos,
			"top_tags": top_tags
		}

		return render(request, self.template, context)


class DashboardAllRepoIndexView(ListView):
	model = Repository
	template_name = "dashboard/index2.html"

	def get_queryset(self):
		queryset = Repository.objects.all()

		search_query = self.request.GET.get('search')
		if search_query:
			queryset = queryset.filter(
				Q(name__icontains=search_query) |
				Q(description__icontains=search_query)
			).order_by('name')
		return queryset
