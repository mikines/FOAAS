import MySQLdb
import secrets
from twython import Twython

db = MySQLdb.connect(host=u'localhost', user=secrets.sqluser(), passwd=secrets.sqlpass(), db=u'fuckoff')
cur = db.cursor()

def post(username):
	cur.execute("SELECT oauth_token,oauth_secret FROM user where username = '%s'" % username)
	temp = cur.fetchone()
	token = temp[0]
	secret = temp[1]
	twitter = Twython(secrets.cons_key(),secrets.cons_sec(),token,secret)
	twitter.update_status(status='testing')
	return ""

post('RiwaRiwana')
