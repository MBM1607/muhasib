''' Module to hold the prayer record screen class and all related functionality '''

from datetime import date

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from prayer_widgets import PrayerOptions


class PrayerRecordsScreen(Screen):
	''' Screen to show the current day's prayer and extra records and to provide an interface to change them '''

	record_lists = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.database = App.get_running_app().database
		self.prayer_record = {}
		self.extra_record = {}

	def create_prayer_list(self):
		''' Populate the prayer records and extra records item lists '''
		record = self.database.get_record(date.today())
		
		self.prayer_record = {"fajr": record[0], "dhuhr": record[1], "asr": record[2],
							"maghrib": record[3], "isha": record[4]}
		# If fast is required then display fast record button
		if record[5]:
			self.extra_record["fast"] = record[6]
		self.extra_record = {"quran": record[7], "hadees": record[8]}
		self.record_lists.create_lists(self, self.prayer_record, self.extra_record)

	def change_extra_record(self, name, value):
		''' Update the extra records of fast, quran and hadees and save to database. '''
		self.extra_record[name] = int(value)
		self.database.update_record(date.today(), **self.prayer_record, **self.extra_record)

	def update_prayer_record(self, name, value):
		''' Update the prayer records and put it on screen and save it to database. '''
		self.prayer_record[name] = value
		self.record_lists.update_prayer_record(name, value)
		self.database.update_record(date.today(), **self.prayer_record, **self.extra_record)	

	def open_prayer_options(self, prayer):
		''' Open the prayer options popup '''
		PrayerOptions(prayer=prayer, base=self).open()