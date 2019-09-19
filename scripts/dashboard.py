''' Module to hold the class for the dashboard '''

from datetime import date

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


class Dashboard(BoxLayout):
	''' Class for the main screen of the app '''

	salah_list = ObjectProperty()
	extra_record_list = ObjectProperty()
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.database = App.get_running_app().database
		self.prayer_record = {}
		self.extra_record = {}

		self.create_prayer_list()

	def create_prayer_list(self):
		''' Populate the prayer records and extra records item lists '''
		record = self.database.get_record(date.today())
		
		self.prayer_record = {"fajr": record[0], "dhuhr": record[1], "asr": record[2],
							"maghrib": record[3], "isha": record[4]}
		if record[5]:
			self.extra_record["fast"] = record[6]
		self.extra_record = {"quran": record[7], "hadees": record[8]}
		self.salah_list.data = [{"name": n.capitalize(), "info": r, "base": self} for n, r in self.prayer_record.items()]
		self.extra_record_list.data = [{"name": n.capitalize(), "active": r, "base": self} for n, r in self.extra_record.items()]

	def change_extra_record(self, name, value):
		''' Update the extra records of fast, quran and hadees and save to database. '''
		self.extra_record[name] = int(value)
		self.database.update_record(date.today(), **self.prayer_record, **self.extra_record)

	def change_prayer_record(self, name, value):
		''' Update the prayer records and put it on screen and save it to database. '''
		self.prayer_record[name] = value
		for child in self.salah_list.children[0].children:
			child.info = self.prayer_record[child.name.lower()]
		self.database.update_record(date.today(), **self.prayer_record, **self.extra_record)		
