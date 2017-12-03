from __future__ import unicode_literals
from django.shortcuts import render
from django.template import Template, Context, RequestContext
from django.contrib.auth import authenticate, logout, login as django_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import cgi, oauth2 as oauth
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
import requests, secrets, MySQLdb
from crontab import CronTab
import re

db = MySQLdb.connect(host=u'localhost', user=secrets.sqluser(), passwd=secrets.sqlpass(), db=u'fuckoff')
cur = db.cursor()

def index(request):
    if request.method == u'POST':
        search = request.POST[u'search']
        r = requests.get(u'https://www.foaas.com/' + search + u'/:from')
        return HttpResponse(r.text)
    t = Template(u'<html><form method="POST">{% csrf_token %}<input type="text" name="search"><input type="submit" value="submit"></form></html>')
    tem = t.render(RequestContext(request))
    return HttpResponse(tem)


consumer = oauth.Consumer(secrets.cons_key(), secrets.cons_sec())
client = oauth.Client(consumer)
request_token_url = u'https://api.twitter.com/oauth/request_token'
access_token_url = u'https://api.twitter.com/oauth/access_token'
authenticate_url = u'https://api.twitter.com/oauth/authenticate'

def login(request, message=u''):
    if request.method == u'POST':
        return twit_login(request)
    if request.user.is_authenticated():
        return HttpResponseRedirect(u'/profile')
    return render(request, u'login.html', {u'message': message})


def twit_login(request):
    resp, content = client.request(request_token_url, u'GET')
    if resp[u'status'] != u'200':
        raise Exception(u'Invalid response from Twitter.')
    request.session[u'request_token'] = dict(cgi.parse_qsl(content))
    url = u'%s?oauth_token=%s' % (authenticate_url, request.session[u'request_token'][u'oauth_token'])
    print url
    return HttpResponseRedirect(url)


@login_required
def twit_logout(request):
    logout(request)
    message = u'You have logged out.'
    return login(request, message=message)


def twit_auth(request):
    token = oauth.Token(request.session[u'request_token'][u'oauth_token'], request.session[u'request_token'][u'oauth_token_secret'])
    if u'oauth_verifier' in request.GET:
        token.set_verifier(request.GET[u'oauth_verifier'])
    client = oauth.Client(consumer, token)
    resp, content = client.request(access_token_url, u'GET')
    if resp[u'status'] != u'200':
        print content
        raise Exception(u'Invalid response from Twitter.')
    access_token = dict(cgi.parse_qsl(content))
    if cur.execute(u"SELECT username FROM user where username = '%s'" % access_token[u'screen_name']):
        user = User.objects.get(username=access_token[u'screen_name'])
    else:
        user = User.objects.create_user(access_token[u'screen_name'], u'%s@twitter.com' % access_token[u'screen_name'], access_token[u'oauth_token_secret'])
        cur.execute(u"INSERT INTO user (username,oauth_token,oauth_secret) VALUES ('%s','%s','%s')" % (access_token[u'screen_name'], access_token[u'oauth_token'], access_token[u'oauth_token_secret']))
        db.commit()
    user = authenticate(username=access_token[u'screen_name'], password=access_token[u'oauth_token_secret'])
    django_login(request, user)
    print access_token[u'screen_name']
    return HttpResponseRedirect(u'/profile')


def get_fuck_text(param):
    url = u'https://www.foaas.com' + param
    r = requests.get(url, headers={u'Accept': u'text/plain'})
    return r.text


def show_profile(request):
    if request.user.is_authenticated():
        user = request.user
    else:
        message = u'You need to login!'
        return render(request, u'login.html', {u'message': message})
    messages = cur.execute(u"SELECT * FROM message WHERE uid = '%s'" % user.username)
    print messages
    return render(request, u'profile.html')


def addtarget(request):
    if request.method == u'POST':
        name = request.POST[u'tname']
        phone = request.POST[u'tphone']
        twitter = request.POST[u'twit']
        cur.execute(u'INSERT INTO target (tname,phone,twitter) values (%s,%s,%s)', (name, phone, twitter))
        db.commit()
    return render(request, u'addtarget.html')


def addmessage(request):
    if request.method == u'POST':
        month = request.POST[u'month']
        try:
            weekday = request.POST[u'weekday'] - 1
            hour = request.POST[u'hour'] - 1
            minute = request.POST[u'minute'] - 1
            sec = request.POST[u'second'] - 1
            day = request.POST[u'day'] + 0
        except:
            weekday = request.POST[u'weekday']
            hour = u'*'
            minute = u'*'
            sec = u'*'
            day = u'*'

        print day
        print u'hour=', hour
        text = request.POST[u'fucksearchs']
        param = inner_get_all_fucks(text)[0]
    return render(request, u'addmessage.html')


@csrf_exempt
def get_all_fucks(request):
    if request.method == u'POST':
        word = request.POST[u'word']
        r = requests.get(u'https://www.foaas.com/fucks', headers={u'Accept': u'text/plain'})
        fucks = r.text
        fucks = fucks.split(u'</td></tr>')
        message = search_all_fucks(word, fucks)
        message = re.sub(u'\\<tr\\>\\<td\\>.+\\<\\/td\\>\\<td\\>', u'', message)
    return render(request, u'allfucks.html', {u'message': message})


def inner_get_all_fucks(word):
    r = requests.get(u'https://www.foaas.com/fucks', headers={u'Accept': u'text/plain'})
    fucks = r.text
    fucks = fucks.split(u'</td></tr>')
    params = search_all_fucks(word, fucks)
    params = re.sub(u'\\<tr\\>\\<td\\>', u'', params)
    params = re.sub(u'\\<\\/td\\>\\<td\\>', u'', params)
    params = re.findall(u'.+\\/\\:from', params)
    return params


def search_all_fucks(word, lst):
    for i in lst:
        if re.search(word, i, re.IGNORECASE):
            i = i.replace(u'Will return content of the form ', u'')
            return i

    return u'sorry, try again'
