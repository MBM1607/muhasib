import sqlite3

import convertdate.islamic as islamic


class Database():
	''' Class to handle all the database related functionality '''

	def __init__(self):
		self.db = sqlite3.connect("data/muhasib.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)

	def create_record(self, date):
		''' Create a record of this date '''

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
	
	def update_record(self, date, fajr="not_prayed", dhuhr="not_prayed", asr="not_prayed", maghrib="not_prayed", isha="not_prayed", fast=False):
		''' Update the prayer record of the date in record table '''

		# Upgrade only if the record exists in database
		if self.get_record(date):
			cursor = self.db.cursor()
			cursor.execute("UPDATE record SET fajr = ?, dhuhr = ? , asr = ?, maghrib = ?, isha = ?, fast = ? WHERE date = ?",
						(fajr, dhuhr, asr, maghrib, isha, fast, date))
			self.db.commit()

	def get_record(self, date):
		''' Get the prayer record of the date from the record table '''

		cursor = self.db.cursor()
		cursor.execute("SELECT * FROM record WHERE date = ?", (date,))
		record = cursor.fetchone()
		if record:
			return record[2:]
		return False
