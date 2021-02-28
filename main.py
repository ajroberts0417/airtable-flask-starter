import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import airtable

from email_service import send_email, build_confirmation_msg

AIRTABLE_BASE = os.getenv('AIRTABLE_BASE')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')

airtable = airtable.Airtable(AIRTABLE_BASE, 'experts', AIRTABLE_API_KEY)

def send_confirmation_email():
    """Send confirmation emails to all the To Process folks.

    Should look something like:
      1. get all records which haven't gotten emails or errors
      2. iterate through the records
      2a. send the emails
      2a1. try: sending the email
      2a2. except: error sending the email
      2a3. mark the error that was found
      2b. mark the records as processed
    
    """
    print("Scheduler is alive!")
    experts = airtable.get_all(view='To process')
    # TODO: remove this when you're satisfied
    print(experts)

    for record in experts:
      email = record['fields']['Email']
      name = record['fields']['Name']

      try:
        msg = build_confirmation_msg(name)
        send_email(email, msg)
        # verify this works to mark the record as processed:
        fields = {'Processed': True}
        airtable.update(record['id'], fields)
      except Exception as e:
        print(f"Error sending email: {str(e)}")
        fields = {'Error': str(e)}
        airtable.update(record['id'], fields)

sched = BackgroundScheduler(daemon=True)
sched.add_job(send_confirmation_email,'interval',seconds=60)
sched.start()

app = Flask('app')

@app.route('/')
def hello_world():
  return 'Hello, World!'

app.run(host='0.0.0.0', port=8080)
