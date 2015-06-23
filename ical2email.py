from icalendar import Calendar
import urllib2
from datetime import datetime, timedelta, date
from pytz import timezone
from email.message import Message
import smtplib
from dateutil import rrule

import config

def send_mail(event, dtstart):
	summary = event.get('summary').to_ical()
	description = event.get('description').to_ical().decode('string_escape').replace('\,', ',').replace('\;',';')
	starttime = dtstart.strftime("%a, %B %d %Y, %H:%M")

	body = "Time & Date: " + starttime + "\n"

	if event.get('location'):
		body += "Location: " + event.get('location').to_ical().decode('string_escape').replace('\,', ',').replace('\;',';') + "\n"

	body += "\n" + description
	subject = "[Event] " + summary + " (" + starttime + ")"

	if event.get('url'):
		url = event.get('url').to_ical()
		body = body + "\nURL: " + url

	msg = Message()
	msg.set_payload(body, "utf-8")
	msg["Subject"] = subject
	msg["From"] = config.MAIL_FROM
	msg["To"] = config.MAIL_TO

	server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(config.SMTP_USER, config.SMTP_PASS)
	text = msg.as_string()
	server.sendmail(config.MAIL_FROM, config.MAIL_TO, text)
	server.quit()	

tz = timezone(config.ICAL_TZ)

req = urllib2.Request(config.ICAL_URL)
response = urllib2.urlopen(req)
data = response.read()

cal = Calendar.from_ical(data)
today = datetime.now(tz).replace(hour=0,minute=0)
time_min = today + timedelta(days=config.DAYS_AHEAD)
time_max = today + timedelta(days=config.DAYS_AHEAD + 1)

for event in cal.walk('vevent'):
	dtstart = event.get('dtstart').dt

	if type(dtstart) is date:
		dtstart = datetime(dtstart.year, dtstart.month, dtstart.day, 0, 0, 0, 0, tz)
	else:
		dtstart = dtstart.astimezone(tz)

	if dtstart > time_min and dtstart < time_max:
		send_mail(event, dtstart)
	else:
		# handle reoccurrences
		if "rrule" in event:
			rule = rrule.rrulestr(event.get('rrule').to_ical(), dtstart=event.get('dtstart').dt)
			for dtstart_rec in rule.between(time_min, time_max):
				send_mail(event, dtstart_rec)
