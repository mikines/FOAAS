# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import requests

def index(request):
#	return HttpResponse("Hello, world. You're at the polls index.")
	if request.method == 'POST':
		search = request.POST['search']
		r = requests.get("https://www.foaas.com/"+search)
		return HttpResponse(r.text)
	return render(request, '/hello.html')
