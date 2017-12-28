from django.http import HttpResponse
from django.shortcuts import render
from ESClass.ESClass import ESClass
import os
# Create your views here.
def index(request):
    es = ESClass('http://localhost:9200/')
    json = es.show_index()
    return HttpResponse(str(json))