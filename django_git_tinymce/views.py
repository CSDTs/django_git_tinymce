from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from extra_views import SortableListMixin, SearchableListMixin
from django_git_tinymce.models import Document, Repo
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django_git_tinymce.forms import DocumentForm


class RepoList(SearchableListMixin, SortableListMixin, ListView):
    sort_fields_aliases = [('name', 'by_name'), ('id', 'by_id'), ('owners', 'by_owners')]
    search_fields = [('application__name', 'iexact')]
    search_split = False
    model = Repo
    paginate_by = 20
    ordering = ["-when"]
    template_name = "repo_list.html"


class DocumentList(SearchableListMixin, SortableListMixin, ListView):
    sort_fields_aliases = [('name', 'by_name'), ('id', 'by_id')]
    search_fields = [('application__name', 'iexact')]
    search_split = False
    model = Document
    paginate_by = 20
    ordering = ["-when"]
    template_name = "document_list.html"

    def get_queryset(self):
        set = Document.approved_projects()
        filter_val = self.request.GET.get('filter')
        if filter_val is not None:
            set = set.filter(application=filter_val,)
        order = self.request.GET.get('orderby')
        if order is not None:
            set = set.order_by(order)
        return set


class DocumentCreate(CreateView):
    model = Document
    form_class = DocumentForm

    def get_success_url(self):
        return reverse('document-update', kwargs={'pk': self.object.id})

    def dispatch(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.request = request
        return super(DocumentCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(DocumentCreate, self).form_valid(form)


class DocumentUpdate(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = "Document_edit.html"

    def post(self, request, *args, **kwargs):
        if 'publish_document' in request.POST:
            super(DocumentUpdate, self).post(request, *args, **kwargs)
            object = super(DocumentUpdate, self).get_object()
            object.save()
            return redirect('approval-create', project_pk=object.pk)
        return super(DocumentUpdate, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(DocumentUpdate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.request = request
        return super(DocumentUpdate, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        object = super(DocumentUpdate, self).get_object()

        # If the object doesn't belong to this user, throw a error 503
        if object.owner != self.request.user or (hasattr(object, 'approval') or object.approved):
            raise PermissionDenied()
        return object


class DocumentDelete(DeleteView):
    model = Document
    success_url = reverse_lazy('project-delete-success')

    def get_object(self, queryset=None):
        object = super(DocumentDelete, self).get_object()
        if not object.owner == self.request.user:
            raise PermissionDenied('this isn\'t your project')
        return object
