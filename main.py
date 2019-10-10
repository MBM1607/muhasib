''' Main python file for running and defining the app object. '''

import json
from datetime import date, datetime

import pytz
from kivy.app import App
from kivy.clock import Clock
from kivy.garden.navigationdrawer import NavigationDrawer
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager

from scripts.calendar import Calendar
from scripts.compass import Compass
from scripts.dashboard import Dashboard
from scripts.custom_widgets import NavigationWidget
from scripts.database import Database
from scripts.prayer_records_screen import PrayerRecordsScreen
from scripts.prayer_times import PrayerTimes
from scripts.prayer_times_screen import PrayerTimesScreen
from scripts.settings import Settings

Builder.load_file("kv/custom_widgets.kv")
Builder.load_file("kv/prayer_widgets.kv")
Builder.load_file("kv/dashboard.kv")
Builder.load_file("kv/locations.kv")
Builder.load_file("kv/settings.kv")
Builder.load_file("kv/compass.kv")
Builder.load_file("kv/prayer_times_screen.kv")
Builder.load_file("kv/prayer_records_screen.kv")
Builder.load_file("kv/calendar.kv")


class MuhasibApp(App):
	''' Muhasib app object '''
	use_kivy_settings = False
	icon = 'data/logo.png'

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.location = ""
		self.tz_name = ""
	
		# Initialize the database
		self.database = Database()
		self.create_database_day()

		# Initializing all the screens and the screen manager
		self.screen_manager = ScreenManager()
		self.navigationdrawer = NavigationDrawer()
		self.dashboard = Dashboard()
		self.calendar = Calendar()
		self.settings = Settings()
		self.compass = Compass()
		self.prayer_times_screen = PrayerTimesScreen()
		self.prayer_records_screen = PrayerRecordsScreen()

		# Add all the screens onto the screen manager
		self.screen_manager.add_widget(self.dashboard)
		self.screen_manager.add_widget(self.calendar)
		self.screen_manager.add_widget(self.settings)
		self.screen_manager.add_widget(self.compass)
		self.screen_manager.add_widget(self.prayer_times_screen)
		self.screen_manager.add_widget(self.prayer_records_screen)

		# Set up the navigation drawer
		self.navigationdrawer.anim_type = "slide_above_anim"
		self.navigationdrawer.opening_transition = "out_sine"
		self.navigationdrawer.opening_transition = "out_sine"
		self.navigationdrawer.set_side_panel(NavigationWidget())
		self.navigationdrawer.set_main_panel(self.screen_manager)

		# Initializing the prayer times and setting its parameters
		self.prayer_times = PrayerTimes()
		self.set_prayer_times_settings()

		# Create interval events
		Clock.schedule_interval(self.prayer_times_screen.update_prayer_labels, 60)
		Clock.schedule_interval(self.day_pass_check, 3600)
	
	@staticmethod
	def utcoffset(tz):
		''' Take the timezone name and return its UTC offset '''
		now = datetime.now(tz=pytz.timezone(tz))
		utc_offset = (now.utcoffset().days * 24) + (now.utcoffset().seconds / 3600)
		return utc_offset
	
	def set_prayer_times_settings(self):
		''' Change the prayer times calculation settings according to app's settings '''
		self.prayer_times.time_format = self.settings.get_config("time_format", "24h")
		self.prayer_times.asr_param = self.settings.get_config("asr_factor", "Standard")
		self.prayer_times.set_method(self.settings.get_config("calc_method", "Muslim World League"))

	def change_location(self, location, lat, lng, alt, tz, update_config=True):
		''' Change all the location data and modify prayer times appropriately '''
		self.location = location
		self.tz_name = tz

		# Update the configuration dictionary of settings with new location data
		if update_config:
			self.settings.config.update({
											"location": location, "latitude": lat,
											"longitude": lng, "altitude": alt, "timezone": tz
										})
		
		# Modify prayer times calculation variables with new data and update the times
		self.prayer_times.lat = lat
		self.prayer_times.lng = lng
		self.prayer_times.alt = alt
		self.prayer_times.timezone = self.utcoffset(tz)
		self.prayer_times_screen.location.text = location
		self.prayer_times_screen.update_prayer_times()
	
	def day_pass_check(self, time):
		''' Check if a day has passed and upgrade the prayer times and records if it has '''
		prayer = self.prayer_times_screen.next_prayer.text.split(":")[0]
		if self.today != date.today() and prayer != "Midnight":
			self.prayer_times.timezone = self.utcoffset(self.tz_name)
			self.create_database_day()
		
	def create_database_day(self):
		''' Create a row in the database for the day '''
		self.today = date.today()
		self.database.create_record(self.today)

	def open_settings(self):
		''' Overriding the kivy settings screen and changing it with a complete custom system.
			This functon open the settings screen'''

		self.screen_manager.current = "settings"

	def open_calendar(self):
		''' Open the calendar screen '''
		self.calendar.populate()
		self.screen_manager.current = "calendar"

	def open_compass(self):
		''' Open the compass screen '''
		self.compass.set_qibla_direction()
		self.screen_manager.current = "compass"
	
	def open_prayer_times(self):
		''' Open the prayer times screen '''
		self.prayer_times_screen.update_prayer_times()
		self.screen_manager.current = "prayer_times"
	
	def open_prayer_records(self):
		''' Open the prayer records screen '''
		self.prayer_records_screen.create_lists()
		self.screen_manager.current = "prayer_records"

	def open_dashboard(self):
		'''Returns the app to the dashboard'''
		self.screen_manager.current = "dashboard"

	def build(self):
		return self.navigationdrawer

if __name__ == "__main__":
	MuhasibApp().run()
