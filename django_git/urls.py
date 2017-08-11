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
from rest_framework import routers

from dashboard.views import DashboardAllRepoIndexView
# from dashboard.views import DashboardView
# from gitusers.views import IndexView

from tags import viewsets as tags_viewsets
from repos import viewsets as repos_viewsets
from gitusers import viewsets as gitusers_viewsets
from analytics import viewsets as analytics_viewsets


router = routers.DefaultRouter()
router.register(r'tag', tags_viewsets.TagViewSet, base_name='api-tag')
router.register(r'repository', repos_viewsets.RepositoryViewSet, base_name='api-repository')
router.register(r'owner', gitusers_viewsets.OwnerViewSet, base_name='api-owner')
router.register(r'taganalytics', analytics_viewsets.TagAnalyticsViewSet, base_name='api-taganalytics')

urlpatterns = [
    # url(r'^$', DashboardView.as_view(), name='index'),
    url(r'^$', DashboardAllRepoIndexView.as_view(), name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^api/v1/', include(router.urls, namespace='apiv1')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^tags/', include('tags.urls', namespace='tags')),
    url(r'^(?P<username>[\w.+-]+)/', include('gitusers.urls')),



]
# use custom template name by providing the template_name argument
# https://docs.djangoproject.com/en/1.11/topics/auth/default/#all-authentication-views
'''
url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='myapp/login.html')),
'''

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
