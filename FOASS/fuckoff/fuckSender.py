# python file to handle all messages sent out
# by twilio and twitter

import sys
import MySQLdb
import secrets
import requests
from twilio.rest import Client
import random
import string
from twython import Twython

db = MySQLdb.connect(host=u'localhost', user=secrets.sqluser(), passwd=secrets.sqlpass(), db=u'fuckoff')
cur = db.cursor()

account_sid = secrets.twi_sid()
auth_token = secrets.twi_tok()

def send():
	mid = sys.argv[1]
	cur.execute("SELECT tid,text,uid FROM message WHERE message_id = '%s'" % mid)
	temp = cur.fetchone()
	tid = temp[0]
	param = temp[1]
	uid = temp[2]
	
	# get the fuck text
	url = 'https://www.foaas.com'+param
	req = requests.get(url,headers={'Accept':'text/plain'})
	text = req.text
	print text
	
	# get the number
	cur.execute("SELECT contact FROM target WHERE tid = '%s'" % tid)
	temp = cur.fetchone()
	contact = temp[0]

	cur.execute("SELECT username FROM user WHERE uid = '%s'" % uid)
	temp = cur.fetchone()
	username = temp[0]
	#print username
	if contact.startswith("@"):
		return tweet(username,contact,text)
	elif contact.startswith("+"):
		return sms(contact,text)
		# send the message
	else:
		return "fucksender error"

def sms(contact,text):
	contact = contact[1:]
	client = Client(account_sid,auth_token)
	message = client.messages.create(
		to = contact,
		from_ = secrets.twi_num(),
		body= text)	
	return ""

def tweet(username,contact,text):
	cur.execute("SELECT oauth_token,oauth_secret FROM user where username = '%s'" % username)
	temp = cur.fetchone()
	token = temp[0]
	secret = temp[1]
	twitter = Twython(secrets.cons_key(),secrets.cons_sec(),token,secret)
	nonce = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(6))
	#print nonce
	send_text = contact + " " +text+nonce
	twitter.update_status(status=send_text)
	return ""


send()
