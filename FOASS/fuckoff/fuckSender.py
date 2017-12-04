# python file to handle all messages sent out
# by twilio and twitter

import sys
import MySQLdb
import secrets
import requests
from twilio.rest import Client

db = MySQLdb.connect(host=u'localhost', user=secrets.sqluser(), passwd=secrets.sqlpass(), db=u'fuckoff')
cur = db.cursor()

account_sid = secrets.twi_sid()
auth_token = secrets.twi_tok()

def send():
	mid = sys.argv[1]
	cur.execute("SELECT tid,text FROM message WHERE message_id = '%s'" % mid)
	temp = cur.fetchone()
	tid = temp[0]
	param = temp[1]
	
	# get the fuck text
	url = 'https://www.foaas.com'+param
	req = requests.get(url,headers={'Accept':'text/plain'})
	text = req.text
	print text
	
	# get the number
	cur.execute("SELECT phone FROM target WHERE tid = '%s'" % tid)
	temp = cur.fetchone()
	phone = temp[0]

	# send the message
	client = Client(account_sid,auth_token)
	message = client.messages.create(
		to = phone,
		from_ = secrets.twi_num(),
		body= text)
	
	return ""

send()
