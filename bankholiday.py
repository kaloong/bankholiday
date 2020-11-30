import datetime, sys
import icalendar
import requests

##today=datetime.date.today()
today=datetime.date(2017,4,17)
def fetch_latest():
	url="https://www.gov.uk/bank-holidays/england-and-wales.ics"
	try:
		req= requests.get(url, allow_redirects=True)

		if req.status_code == 200:
			with open('bankholiday.ics','wb') as f:
				f.write(req.content)
			return req.content
	except requests.exceptions.ConnectionError as e:
		print("Error: Connection Error.\n",e)
	except requests.exceptions.HTTPError as e:
		print("Error: HTTP Error:\n",e)
	except requests.exceptions.RequestException as e:
		print("Error: Something is wrong.\n", e)
	except requests.exceptions.Timeout as e:
		print("Error: Connection timed out.\n",e)
	sys.exit()

data=fetch_latest()
ical=icalendar.Calendar.from_ical(data)
for component in ical.walk():
	if component.name =="VEVENT" and component.get('dtstart').dt == today:
		print(component.get('summary'))
			