from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404


class RepoDetailFieldLookupMixin(object):
    """
    Apply this mixin to any view or viewset to get multiple
    field filtering based on a `lookup_fields` attribute, instead
    of the default single field filtering.
    """
    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}

        for field in self.lookup_fields:
            if field == "owner" and self.kwargs[field]:
                try:
                    User = get_user_model()
                    owner_obj = User.objects.get(username=self.kwargs[field])
                    filter[field] = owner_obj
                except:
                    raise Http404("user does not exist")

            elif self.kwargs[field]:
                filter[field] = self.kwargs[field]

        return get_object_or_404(queryset, **filter)
