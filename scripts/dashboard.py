''' Module to hold the class for the dashboard '''

from datetime import date

from kivy.app import App
from kivy.properties import DictProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout


class Dashboard(BoxLayout):
	''' Class for the main screen of the app '''

	prayer_record = DictProperty()
	salah_list = ObjectProperty()
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.app = App.get_running_app()

	def create_prayer_list(self):
		''' Create the list for prayer records '''

		record = self.app.database.get_prayer_record(date.today())
		self.prayer_record = {"fajr": record[0], "dhuhr": record[1], "asr": record[2],
							"maghrib": record[3], "isha": record[4]}

		self.salah_list.data = [{"name": n.capitalize(), "info": r, "base": self} for n, r in self.prayer_record.items()]

	def on_prayer_record(self, instance, value):
		''' Update the records of salah list '''
		for x in self.salah_list.children[0].children:
			x.info = self.prayer_record[x.name.lower()]
		
		self.app.database.update_prayer_record(date.today(), **self.prayer_record)
