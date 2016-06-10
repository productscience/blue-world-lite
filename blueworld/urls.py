"""blueworld URL Configuration

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
from django.conf.urls import url, include
from django.contrib import admin
import join.views


urlpatterns = [
    url(r'^$', join.views.home, name='home'),
    url(r'^join/$', join.views.join, name='join'),
    url(r'^join/choose-bags/$', join.views.choose_bags, name='join_choose_bags'),
    url(r'^join/collection-point/$', join.views.collection_point, name='join_collection_point'),
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('allauth.urls')),
    url(r'^hijack/', include('hijack.urls')),
    url(r'^dashboard/$', join.views.dashboard, name='dashboard'),
]
