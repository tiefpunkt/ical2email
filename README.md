# ical2email - send email reminders for iCal meetings

For the @munichmakerlab, we wanted to send reminders for meetings in our calendar to the hackerspace mailing list. So I wrote a tool that does exactly that.

For the Munich Maker Lab, we use it with a Google Calendar feed, but it likely works with all other kinds of iCal feeds as well.

The script is best run daily as a cronjob, and will send out one email for each event happening in a number of days from today, as configured in the `DAYS_AHEAD` variable in the config file.

## Setup
```
# Clone the repository
git clone https://github.com/tiefpunkt/ical2email.git
cd ical2email

# create virtual environment
virtualenv env
./env/bin/pip install -r requirements.txt

# create config file
cp config.py.sample config.py
vi config.py

# Testrun
./env/bin/python ical2email.py
```

## Similar projects
* [phil](https://pypi.org/project/phil/) seems to do a similar thing, but I just found out about it in 2021.

## License
Licensed under the MIT License, see [LICENSE](./LICENSE) for details.
