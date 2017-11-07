"""django_git URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.generic.base import RedirectView
from rest_framework import routers

from dashboard.views import MenuView
from tags import viewsets as tags_viewsets
from repos import viewsets as repos_viewsets
from gitusers import viewsets as gitusers_viewsets

from ckeditor_uploader.views import upload, browse


router = routers.DefaultRouter()
router.register(r'tag', tags_viewsets.TagViewSet, base_name='api-tag')
router.register(r'repository',
                repos_viewsets.RepositoryViewSet, base_name='api-repository')
router.register(r'owner', gitusers_viewsets.OwnerViewSet, base_name='api-owner')
router.register(r'user', gitusers_viewsets.UserView, 'list')


urlpatterns = [
    # url(r'^$', DashboardView.as_view(), name='index'),
    url(r'^$', MenuView.as_view(), name='index'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r'^favicon\.ico/$', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r'^culture/img/nsf\.png/$', RedirectView.as_view(url='/static/img/nsf.png')),
    url(r'^culture/img/CSDT.LOGO2-SMALL\.jpg/$', RedirectView.as_view(url='/static/img/CSDT.LOGO2-SMALL.jpg')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^upload/', login_required(upload), name='ckeditor_upload'),
    url(r'^browse/', never_cache(login_required(browse)), name='ckeditor_browse'),
    url(r'^api/v1/', include(router.urls, namespace='apiv1')),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^tags/', include('tags.urls', namespace='tags')),
    url(r'^api/v1/files/(?P<resource_id>\d+)[/]?$',
        gitusers_viewsets.FilesView.as_view(), name='my_rest_view'),
    url(r'^api/v1/files/(?P<resource_id>\d+)/(?P<directories>.*)/$',
        gitusers_viewsets.FilesView.as_view(), name='my_rest_view'),




]
# use custom template name by providing the template_name argument
# https://docs.djangoproject.com/en/1.11/topics/auth/default/#all-authentication-views
'''
url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='myapp/login.html')),
'''

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += url(r'^(?P<username>[\w.+-]+)/', include('gitusers.urls')),
