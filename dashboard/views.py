from django.db.models import Q
from django.views.generic.list import ListView

from repos.models import Repository


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


class MenuView(ListView):
    model = Repository
    template_name = "dashboard/menu.html"
