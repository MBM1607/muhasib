import sqlite3
from datetime import date, timedelta

import convertdate.islamic as islamic
from helpers import daterange

class Database():
	'''Class to handle all the database related functionality'''

	def __init__(self):
		self.db = sqlite3.connect("data/muhasib.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)

	def create_record(self, date):
		'''Create a record of this date'''

		# Only create if record doesn't exists
		if not self.get_record(date):
			cursor = self.db.cursor()
			# Check for ramazan
			if islamic.from_gregorian(date.year, date.month, date.day)[1] == 9:
				fast_required = True
			else:
				fast_required = False
			cursor.execute("INSERT INTO record(date, fast_required) VALUES(?, ?)", (date, fast_required))
			self.db.commit()
	
	def update_record(self, date, fajr="Not Prayed", dhuhr="Not Prayed", asr="Not Prayed", maghrib="Not Prayed",
							isha="Not Prayed", fast=0, quran=0, hadees=0):
		'''Update the prayer record of the date in record table'''

		# Upgrade only if the record exists in database
		if self.get_record(date):
			cursor = self.db.cursor()
			cursor.execute('''UPDATE record SET fajr = ?, dhuhr = ? , asr = ?,
							maghrib = ?, isha = ?, fast = ?, quran_study = ?,
							hadees_study = ? WHERE date = ?''',
						(fajr, dhuhr, asr, maghrib, isha, fast, quran, hadees, date))
			self.db.commit()

	def get_record(self, date):
		'''Get the prayer record of the date from the record table'''
		cursor = self.db.cursor()
		cursor.execute("SELECT fajr, dhuhr, asr, maghrib, isha, fast_required, fast, quran_study, hadees_study FROM record WHERE date = ?", (date,))
		record = cursor.fetchone()
		return record
	
	def get_prayer_record_range(self, date, max_date=date.today()):
		'''Get the prayer records of all days after the specified date and upto the maximum date'''

		# Loop through the date range and ensure that record for all the dates exist
		for dt in daterange(date, max_date + timedelta(1)):
			self.create_record(dt)

		cursor = self.db.cursor()
		cursor.execute("SELECT fajr, dhuhr, asr, maghrib, isha FROM record WHERE date >= ? AND date <= ? ", (date, max_date))
		return cursor.fetchall()
