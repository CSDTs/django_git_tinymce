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

from dashboard.views import DashboardView, DashboardAllRepoIndexView
# from gitusers.views import IndexView


urlpatterns = [
	# url(r'^$', DashboardView.as_view(), name='index'),
	url(r'^$', DashboardAllRepoIndexView.as_view(), name='index'),
	url(r'^admin/', admin.site.urls),
	url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
	url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),

	url(r'^tinymce/', include('tinymce.urls')),

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
