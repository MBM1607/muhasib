import sqlite3

class Database():
	''' Class to handle all the database related functionality '''

	def __init__(self):
		self.db = sqlite3.connect("muhasib.db", detect_types=sqlite3.PARSE_DECLTYPES)

	# Create a prayer record of this date
	def create_prayer_record(self, date):
		# Only create if record doesn't exists
		if not self.get_prayer_record(date):
			cursor = self.db.cursor()
			cursor.execute("INSERT INTO prayer_record(date) VALUES(?)", (date,))
			self.db.commit()
	
	# Update the prayer record of the date in prayer_record table
	def update_prayer_record(self, date, fajr="not_prayed", dhuhr="not_prayed", asr="not_prayed", maghrib="not_prayed", isha="not_prayed"):

		# Upgrade only if the record exists in database
		if self.get_prayer_record(date):
			cursor = self.db.cursor()
			cursor.execute("UPDATE prayer_record SET fajr = ?, dhuhr = ? , asr = ?, maghrib = ?, isha = ? WHERE date = ?",
						(fajr, dhuhr, asr, maghrib, isha, date))
			self.db.commit()

	# Get the prayer record of the date from the prayer_record table
	def get_prayer_record(self, date):
		cursor = self.db.cursor()
		cursor.execute("SELECT * FROM prayer_record WHERE date = ?", (date,))

		return cursor.fetchone()