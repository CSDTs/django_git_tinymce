from django.views import View
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
			# this requires login
			# tag_analytics = request.user.taganalytics_set.all().order_by("-count")
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