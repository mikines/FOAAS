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

def login(request, message=''):
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
    return HttpResponseRedirect('/')


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
		return login(request,message)
	cur.execute("SELECT uid from user where username = '%s'" % user.username)
	uid = cur.fetchone()
	cur.execute(u"SELECT contact,text,frequency FROM message JOIN target ON message.tid=target.tid WHERE message.uid = '%s'" % uid)
	user_targets_sms = cur.fetchall()
	user_target_contact = []
	user_target_mess = []
	user_target_freq = []
	for i in user_targets_sms:
		user_target_contact += [i[0]]
		user_target_mess += [i[1]]
		user_target_freq += [i[2]]
	user_target_plat = []
	for i in user_target_contact:
		if i.startswith('@'):
			user_target_plat += ["Twitter"]
		elif i.startswith('+'):
			user_target_plat += ["Phone"]
		else:
			return "showprofile error"
	
	#print "mess= ", user_target_mess
	#print "phone= ", user_target_phone
	user_targets_contact_mess = zip(user_target_plat,user_target_contact,user_target_mess,user_target_freq)
	#cur.execute("SELECT ")
	#user_targets_phone = cur.fetchall()
	#for i in user_targets_sms[1]:
	#	i = get_fucks_text(i) #replace /.. with actual text
	#print user_targets_sms
	if request.method == 'POST':
		try:
			weekday = str(int(request.POST[u'weekday']))
		except:
			weekday = '*'
		try:
			hour = str(int(request.POST[u'hour']) + 0)
		except:
			hour = u'*'
		try:
			minute = str(int(request.POST[u'minute']) + 0)
		except:
			minute = u'*'
		try:
			day = str(int(request.POST[u'day']) + 0)
		except:
			day = u'*'
		try:
			month = str(int(request.POST[u'month']) + 0)
		except:
			month = '*'
		contact = request.POST['phone']
		frequency = minute + " " + hour + " "  + day + " " + month + " " + weekday
		#print frequency
		text = request.POST[u'fucksearchs']
		param = inner_get_all_fucks(text)[0]
		# MAKE MESSAGE TUPLE
		# get tid from phone number
		cur.execute('SELECT uid from user where username = "%s"' % request.user.username)
		uid = cur.fetchone()[0]
		print "contact=", contact
		cur.execute('SELECT tid FROM target WHERE contact = "%s"' % contact)
		tid = cur.fetchone()[0]
		cur.execute('SELECT message_id FROM message WHERE uid = "%s" AND tid = "%s"' % (uid,tid))
		mid = cur.fetchone()[0]
		
		my_cron = CronTab(user=secrets.cron_user())
		if cur.execute("SELECT message_id FROM message WHERE uid = '%s' AND tid = '%s'" % (uid,tid)):
			cur.execute("UPDATE message SET text = '%s', frequency = '%s' WHERE uid = '%s' AND tid = '%s'" % (param,frequency,uid,tid))
			my_cron.remove_all(comment='%s' % mid)
		else:
			cur.execute('INSERT INTO message (text,uid,tid,frequency) VALUES ("%s","%s","%s","%s")' % (param,uid,tid,frequency))
		db.commit()
		#if cur.execute('SELECT ') # NEED TARGET
		#for job in my_cron:
	#		print job
		# get mid
		# get command
		job = my_cron.new(command= 'python /home/FOAAS/FOASS/fuckoff/fuckSender.py %s' % mid,comment='%s' % mid)
		#print "Freq ", frequency
		job.setall(frequency)
		my_cron.write()
	return render(request, u'profile.html',{'user_targets_phone_mess':user_targets_contact_mess})#{'user_targets_sms':user_targets_sms,'user_target_phone':user_target_phone})

@login_required
def addtarget(request):
	if request.method == u'POST':
		name = request.POST[u'tname']
		#print name
		#phone = request.POST[u'tphone']
		#twitter = request.POST[u'twit']
		contact = ""
		try: 
			twitter = request.POST['twit']
			contact = "@" + twitter
		except:
			try:
				phone = request.POST['tphone']
				contact = "+" + phone
			except:
				return "addtarget error"
		#elif request.POST['tphone']:
		#	contact = "+" + phone
		#else:
		#	return "addtarget error"
		cur.execute(u'INSERT INTO target (tname,contact) values (%s,%s)', (name, contact))
		db.commit()
		cur.execute("SELECT tid FROM target WHERE contact = '%s'" % (contact))
		tid = cur.fetchone()
		#print tid
		cur.execute("SELECT uid FROM user WHERE username = '%s'" % request.user.username)
		uid = cur.fetchone()
		#print "uid= ", uid
		cur.execute("INSERT INTO message (uid,tid) VALUES (%s,%s)", (uid,tid))
		db.commit()
	return render(request, u'addtarget.html')

@login_required
def addmessage(request):
    #if request.method == u'POST':
                #print day
        #print u'hour=', hour
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
