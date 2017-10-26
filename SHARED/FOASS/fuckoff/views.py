# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import Template,Context

# Create your views here.

from django.http import HttpResponse
import requests

def index(request):
#	return HttpResponse("Hello, world. You're at the polls index.")
	if request.method == 'POST':
		search = request.POST['search']
		r = requests.get("https://www.foaas.com/"+search)
		return HttpResponse(r.text)
	#return render(request, 'hello.html')
	#t = Template(<form method="POST"><input type="text" name="search"><input type="submit"></form>)
	#html = t.render(Context())
	html = '<html><form method="POST"><input type="text" name="search"><input type="submit" value="submit"></form></html>'
	return HttpResponse(html)
