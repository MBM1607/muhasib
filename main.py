''' Main python file for running and defining the app object. '''

import json
from datetime import date, datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import DictProperty
from kivy.garden.navigationdrawer import NavigationDrawer
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager
from pytz import timezone

from scripts.calendar_screen import CalendarScreen
from scripts.qibla import QiblaScreen
from scripts.dashboard import Dashboard
from scripts.custom_widgets import NavigationWidget
from scripts.database import Database
from scripts.prayer_records_screen import PrayerRecordsScreen
from scripts.prayer_times import PrayerTimes
from scripts.prayer_times_screen import PrayerTimesScreen
from scripts.graphs_screen import PrayerGraphsScreen
from scripts.settings import SettingsScreen
from scripts.locations import LocationForm
from scripts.helpers import utcoffset

Builder.load_file("kv/custom_widgets.kv")
Builder.load_file("kv/prayer_widgets.kv")
Builder.load_file("kv/dashboard.kv")
Builder.load_file("kv/locations.kv")
Builder.load_file("kv/settings.kv")
Builder.load_file("kv/qibla.kv")
Builder.load_file("kv/prayer_times_screen.kv")
Builder.load_file("kv/prayer_records_screen.kv")
Builder.load_file("kv/graphs_screen.kv")
Builder.load_file("kv/calendar_screen.kv")


class MuhasibApp(App):
	''' Muhasib app object '''
	use_kivy_settings = False
	icon = 'data/logo.png'
	settings = DictProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)


		# Load the setting configuration setting its prayer time parameters
		self.prayer_times = PrayerTimes()
		self.load_settings()

		# Initialize the database
		self.database = Database()
		self.create_database_day()

		# Initializing all the screens and the screen manager
		self.screen_manager = ScreenManager()
		self.navigationdrawer = NavigationDrawer()
		self.location_form = LocationForm()

		# Add all the screens onto the screen manager
		self.screen_manager.add_widget(Dashboard())
		self.screen_manager.add_widget(PrayerTimesScreen())
		self.screen_manager.add_widget(PrayerRecordsScreen())
		self.screen_manager.add_widget(PrayerGraphsScreen())
		self.screen_manager.add_widget(CalendarScreen())
		self.screen_manager.add_widget(QiblaScreen())
		self.screen_manager.add_widget(SettingsScreen())

		# Set up the navigation drawer
		self.navigationdrawer.anim_type = "slide_above_anim"
		self.navigationdrawer.opening_transition = "out_sine"
		self.navigationdrawer.opening_transition = "out_sine"
		self.navigationdrawer.set_side_panel(NavigationWidget())
		self.navigationdrawer.set_main_panel(self.screen_manager)

		# Create interval events
		Clock.schedule_once(lambda _: self.location_check())
		Clock.schedule_interval(lambda _: self.day_pass_check(), 3600)
	
	def get_current_time(self):
		''' Get the UTC time of the timezone currently set in settings '''
		return datetime.now(tz=timezone(self.settings["timezone"]))

	def get_formatted_time(self, time):
		''' Take a time and return it in the string format of the configuration '''
		if self.settings["time_format"] == "24h":
			return time.strftime("%H:%M")
		else:
			return time.strftime("%I:%M %p")

	def set_prayer_times_settings(self):
		''' Change the prayer times calculation settings according to app's settings '''
		self.prayer_times.show_imsak_time = self.settings["show_imsak_time"]
		self.prayer_times.time_format = self.settings["time_format"]
		self.prayer_times.asr_param = self.settings["asr_factor"]
		self.prayer_times.set_method(self.settings["calc_method"])

	def set_prayer_time_location(self):
		''' Change the prayer time location variables according to the settings '''
		self.prayer_times.lat = self.settings["latitude"]
		self.prayer_times.lng = self.settings["longitude"]
		self.prayer_times.alt = self.settings["altitude"]
		self.prayer_times.timezone = utcoffset(self.settings["timezone"])

	def change_location(self, location, lat, lng, alt, tz):
		''' Change all the location data and modify prayer times appropriately '''

		self.settings["location"] = location
		self.settings["latitude"] = lat
		self.settings["longitude"] = lng
		self.settings["altitude"] = alt
		self.settings["timezone"] = tz

	def location_check(self):
		''' Check if location is present, if not open the form to get location '''

		if self.location_data_present():
			self.set_prayer_time_location()
		else:
			self.location_form.open()

	def location_data_present(self):
		''' Check if the location data is in the configuration '''
		if self.settings["location"] and self.settings["latitude"] and self.settings["longitude"] and self.settings["timezone"]:
			return True
		else:
			return False

	def load_settings(self):
		''' Load the setttings configuration from the file and make the file if it doesn't exist '''
		try:
			with open("data/settings.json", "r") as json_file:
				self.settings = json.load(json_file)
		except FileNotFoundError:
			self.settings = {
							"latitude": 0, "longitude": 0, "altitude": 0,
							"location": "", "calc_method": "Muslim World League",
							"asr_factor": "Standard", "time_format": "24h",
							"show_imsak_time": True
							}
			self.save_settings()

	def save_settings(self):
		''' Save the settings in a json file '''
		with open("data/settings.json", "w") as json_file:
			json.dump(self.settings, json_file)

	def on_settings(self, instance, value):
		''' When config changes then upgrade prayer time configuration and save the settings '''
		self.set_prayer_times_settings()
		self.save_settings()

	def day_pass_check(self):
		''' Check if a day has passed and upgrade the prayer times and records if it has '''
		if self.today != date.today():
			self.prayer_times.timezone = utcoffset(self.settings["timezone"])
			self.create_database_day()
		
	def create_database_day(self):
		''' Create a row in the database for the day '''
		self.today = date.today()
		self.database.create_record(self.today)

	def build(self):
		return self.navigationdrawer

if __name__ == "__main__":
	MuhasibApp().run()
