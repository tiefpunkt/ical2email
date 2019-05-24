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

events = []

for event in cal.walk('vevent'):
	dtstart = event.get('dtstart').dt

	if type(dtstart) is date:
		dtstart = datetime(dtstart.year, dtstart.month, dtstart.day, 0, 0, 0, 0, tz)
	else:
		dtstart = dtstart.astimezone(tz)

	if dtstart > time_min and dtstart < time_max:
		#send_mail(event, dtstart)
		events.append((event, dtstart))
	else:
		# handle reoccurrences
		if "rrule" in event:
			rule = rrule.rrulestr(event.get('rrule').to_ical(), dtstart=event.get('dtstart').dt)
                        rule = rrule.rruleset()
                        rule.rrule(rrule.rrulestr(event.get('rrule').to_ical(), dtstart=event.get('dtstart').dt))
                                                                        
                        if "exdate" in event:
                                exdates = event.get("exdate")
                                if not isinstance(exdates, list):
                                        exdates = [exdates]
                                for exdate in exdates:
                                        rule.exdate(exdate.dts[0].dt)

			for dtstart_rec in rule.between(time_min, time_max):
				#send_mail(event, dtstart_rec)
				events.append((event, dtstart_rec))

def check_for_modified_reoccurences(old_items, new_item):
	# check all events for duplicate UIDs
	for n, item in enumerate(old_items):
		if item[0].get('uid') == new_item[0].get('uid'):
			# Duplicate UID found
			# The original item has no "RECURRENCE-ID" set, the updated one does
			if "RECURRENCE-ID" in new_item[0]:
				# new item the updated one
				# remove the old entry, fill in the new one
				del old_items[n]
				old_items.append(new_item)
			# if the old one is the updated one, just ignore the new item and move on
			return old_items

	# first item, or simply duplicate UIDs found
	old_items.append(new_item)
	return old_items

events = reduce(check_for_modified_reoccurences, events, [])

for event in events:
	send_mail(event[0], event[1])
