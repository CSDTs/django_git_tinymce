from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Tag
# from analytics.models import TagAnalytics


class TagListView(ListView):
    model = Tag


class TagDetailView(DetailView):
    model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagDetailView, self).get_context_data(**kwargs)

        # if self.request.user.is_authenticated():
        #     user = self.request.user
        #     tag = self.get_object()
        #     tag_analytics_obj = TagAnalytics.objects.add_count(user, tag)

        return context
