"""CloManager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from app import views
admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index2$', views.index2, name="index2"),
    url(r'^home$', views.home, name='home'),
    url(r'^complete$', views.complete, name = "complete"),
    url(r'^search$', views.search, name="search"),
    url(r'^control$', views.control, name = "search"),
    url(r'^rank$', views.rank, name = "rank"),
    url(r'^suggest$', views.suggest, name = "suggest"),
    url(r'^admin/', include(admin.site.urls)),
]
