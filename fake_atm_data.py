# GS, 2017-09-25
#
# generate fake ATM data
#
# output csv schema: atm_id,datetime,amount
#
# generating 10 fake ATMs:
#
# $ time python3.6 fake_atm_data.py 
#
# real	0m27.081s
# user	0m26.823s
# sys	0m0.213s
#
# $ ls -hal fake_atm_data.csv 
# -rw-r--r--  1 garrysteedman  REG1\Domain Users    29M Sep 25 22:59 fake_atm_data.csv

import csv
from faker import Faker
import random

fake = Faker()

def generate_atmid(atm_id):
	atm_ids = []
	for i in range(100000):
		atm_ids.append(atm_id)
	return atm_ids

def generate_dates():
	dates = []
	for i in range(100000):
		date = fake.date_time_between(start_date='-3y', end_date='now', tzinfo=None)
		dates.append(date.isoformat())
	return dates

def generate_amounts():
	amounts = []
	for i in range(100000):
		amount = random.randint(0, 10000)
		amounts.append(amount)
	return amounts

def generate_atm_data():
	atm_ids = generate_atmid(fake.pyint())
	dates = generate_dates()
	amounts = generate_amounts()
	atm_data = zip(atm_ids, dates, amounts)
	return atm_data

def write_atm_data():
	with open('fake_atm_data.csv', 'a') as f:
		fieldnames = ['atm_id','datetime','amount']
		writer = csv.writer(f,  delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(fieldnames)
		for x in range(1):
			atm_data = generate_atm_data()		
			writer.writerows(atm_data)

if __name__ == '__main__':
	write_atm_data()
