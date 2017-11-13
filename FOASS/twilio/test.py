from twilio.rest import Client
import twi,twi_nums

account_sid = twi.sid()
auth_token = twi.tok()

def send():
  client = Client(account_sid,auth_token)

  message = client.messages.create(
    to=twi_nums.get_number(),
    from_=twi_nums.from_num(),
    body="testing")

#print message.sid

send()
