from flask import Flask
from flask import Blueprint
from flask import jsonify
import sys
import icalendar
import requests
import calendar
from datetime import date, datetime, timedelta
from pathlib import Path

app = Flask(__name__)

"""Global scope"""
v1=Blueprint("version1","version1")
v2=Blueprint("version2","version2")
##today=date.today()
today=date(2017,01,01)


"""
Version 1

What are the questions?

what should bankholiday check do?

is today a bankholiday? yes or no?

is today a working day?

is tomorrow a working day?

was yesterday a working day?

when is the next working day?

when is the previous working day?


is current day a bankholiday?
	if yes 
   is today a weekend?
	   if weekend 
	   is today saturday? 
		   if saturday set offset to 2
		   otherwise set offset to 1
	   return weekend
   return weekday
if no
   is today a weekday or weekend?
   if weekday return normal weekday.
   or return weekend.

"""


@v1.route('/curr',methods=['GET'])
def get_curr_biz_day():
	return check_bank_holiday(today)

@v1.route('/last',methods=['GET'])
def get_last_biz_day():
	return check_bank_holiday(today-timedelta(offset))

@v1.route('/next',methods=['GET'])
def get_next_biz_day():
	if today.weekday() not in range(calendar.MONDAY,calendar.FRIDAY):
		if today.weekday() == calendar.SATURDAY:
			offset = 2
		else:
			offset = 1
	result = check_bank_holiday( today+timedelta(offset) )
	if result is not None:
		return jsonify({'+>':result})
	return jsonify({'->':today+timedelta(offset)})

@v1.route('/', methods=['GET'])
def index():
	return jsonify({'App':'Business date resolver api version 1'})

"""
Version 2
"""
@v2.route('/curr',methods=['GET'])
def get_curr_biz_day():
	return get_bank_holiday(today)

@v2.route('/last',methods=['GET'])
def get_last_biz_day():
	return jsonify({'last business date':'2020-12-17'})

@v2.route('/next',methods=['GET'])
def get_next_biz_day():
	return jsonify({'next business date':'2020-12-19'})

@v2.route('/', methods=['GET'])
def index():
	return jsonify({'App':'Business date resolver api version 2'})


def fetch_bank_holiday_file():
	url="https://www.gov.uk/bank-holidays/england-and-wales.ics"
	bank_holiday_file="bankholiday.ics"
	try:
		"""Check if file already exists"""
		if Path('bankholiday.ics').exists():
			""" Need to check how old is the file if it is too old download new one"""
			with open(bank_holiday_file,'rb') as f:
				return f.read()

		"""File doesn't exists, download new one"""
		req= requests.get(url, allow_redirects=True)
		if req.status_code == 200:
			with open(bank_holiday_file,'wb') as f:
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


"""
This really checks if variable 'today' is a bank holiday.
for python3 use: def get_bank_holiday( target_date: datetime.date ):
"""
def check_bank_holiday( target_date):

	###target_date = datetime.date.today()
    ###today=datetime.date(2017,4,17)
	data = fetch_bank_holiday_file()
	ical = icalendar.Calendar.from_ical(data)
	result = None
	for component in ical.walk():
		if component.name =="VEVENT" and component.get('dtstart').dt == target_date:
			result = component.get('summary')
			return result
	return result
	"""
			return jsonify({"Current date is {} bank holiday".format(result.encode('ascii','ignore').decode('ascii')) : "{}".format(target_date)})
	return jsonify({'Current business date':"{}".format(target_date)})
	"""

def main():
		
	app.register_blueprint(v1,url_prefix="/v1")
	app.register_blueprint(v2,url_prefix="/v2")
	app.register_blueprint(v1,url_prefix="/")
	app.run(host='0.0.0.0', port='3000')

if __name__ == '__main__':
	main()
