# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from requests import *

def index(request):
#	return HttpResponse("Hello, world. You're at the polls index.")
	url = "https://www.foaas.com/asshole/:from me"
	return requests.get(url)
