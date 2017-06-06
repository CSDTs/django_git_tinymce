"""django_git_tinymce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django_git_tinymce.views import RepoDetail, DocumentList, DocumentCreate, DocumentUpdate, DocumentDelete
from django.views import static
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^repos/(?P<user>[-\w]+)/(?P<slug>[-\w]+)/$', RepoDetail.as_view(), name="repo-detail"),
    # url(r'^repos/', RepoList.as_view(), name='repo-list'),
    url(r'^docs/(?P<path>.*)$', DocumentList.as_view(), name='docs-list'),
    url(r'^newdoc/(?P<path>.*)$', DocumentCreate.as_view(), name='docs-create'),
    url(r'^editdoc/(?P<path>.*)$', DocumentUpdate.as_view(), name='docs-update'),
    url(r'^deldoc/(?P<path>.*)$', DocumentDelete.as_view(), name='docs-delete'),
    url(r'^(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_URL + 'git', }),
]
