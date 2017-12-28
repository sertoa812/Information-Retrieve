'''
Created on 2016年4月1日

@author: dc
'''
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index,name = 'index'),
]

