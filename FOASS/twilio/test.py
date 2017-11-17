from twilio.rest import Client
import twi,twi_nums

account_sid = twi.sid()
auth_token = twi.tok()

client = Client(account_sid,auth_token)
def send():
  message = client.messages.create(
    to=twi_nums.get_number(),
    from_=twi_nums.from_num(),
    body="testing")

#print message.sid

def add_caller(number):
  validation_request = client.validation_requests.create(number,friendly_name="test")
  print validation_request.validation_code

add_caller(twi_nums.get_test())
#send()


