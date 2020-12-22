from flask import Flask
from flask import Blueprint
from flask import jsonify
import datetime, sys
import icalendar
import requests
from pathlib import Path

app = Flask(__name__)

"""Global scope"""
v1=Blueprint("version1","version1")
v2=Blueprint("version2","version2")
##today=datetime.date.today()
today=datetime.date(2017,4,17)

"""
Version 1
"""

@v1.route('/curr',methods=['GET'])
def get_curr_biz_day():
	return get_bank_holiday()


@v1.route('/prev',methods=['GET'])
def get_prev_biz_day():
	return jsonify({'Previous business date':'20201217'})

@v1.route('/last',methods=['GET'])
def get_last_biz_day():
	return jsonify({'Last business date':'20201219'})

@v1.route('/', methods=['GET'])
def index():
	return jsonify({'App':'Business date resolver api version 1'})

"""
Version 2
"""
@v2.route('/curr',methods=['GET'])
def get_curr_biz_day():
	return jsonify({'Current business date':'2020-12-18'})

@v2.route('/prev',methods=['GET'])
def get_prev_biz_day():
	return jsonify({'Previous business date':'2020-12-17'})

@v2.route('/last',methods=['GET'])
def get_last_biz_day():
	return jsonify({'Last business date':'2020-12-19'})

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

def get_bank_holiday():
	data = fetch_bank_holiday_file()
	ical = icalendar.Calendar.from_ical(data)
	for component in ical.walk():
		if component.name =="VEVENT" and component.get('dtstart').dt == today:
			result = component.get('summary')
			return jsonify({'Current date is {}'.format(result):"{}".format(today)})
	"""Check other logic e.g. is today Monday - Friday? """
	return jsonify({'Current business date':"{}".format(today)})

def main():
		
	app.register_blueprint(v1,url_prefix="/v1")
	app.register_blueprint(v2,url_prefix="/v2")
	app.register_blueprint(v2,url_prefix="/")
	app.run(host='0.0.0.0', port='3000')

if __name__ == '__main__':
	main()
