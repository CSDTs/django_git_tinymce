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

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^password_change/$', auth_views.PasswordChangeView.as_view(), name='password_change'),
    url(r'^password_change_done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset_done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^password_reset_confirm/$', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^password_reset_complete/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    url(r'^tags/', include('tags.urls', namespace='tags')),
    url(r'^(?P<username>[\w.+-]+)/', include('gitusers.urls', namespace='owner')),

    # url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^create/$', views.RepositoryCreateView.as_view(), name='create'),
    # url(r'^(?P<slug>[-\w]+)/$', views.RepositoryDetailView.as_view(), name='detail'),
    # url(r'^(?P<slug>[-\w]+)/delete/$', views.RepositoryDeleteView.as_view(), name='delete'),
    # url(r'^(?P<slug>[-\w]+)/setting/$', views.RepositoryUpdateView.as_view(), name='setting'),
]
# use custom template name by providing the template_name argument
# https://docs.djangoproject.com/en/1.11/topics/auth/default/#all-authentication-views
'''
url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='myapp/login.html')),
'''

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)