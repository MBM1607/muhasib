''' Main python file for running and defining the app object. '''

import json
from datetime import date

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.properties import DictProperty, ListProperty
from requests_cache import install_cache
from scripts.calendar import Calendar
from scripts.compass import Compass
from scripts.dashboard import Dashboard
from scripts.database import Database
from scripts.prayer_times import PrayerTimes
from scripts.prayer_times_screen import PrayerTimesScreen
from scripts.settings import Settings

Builder.load_file("kv/custom_widgets.kv")
Builder.load_file("kv/dashboard.kv")
Builder.load_file("kv/prayer_widgets.kv")
Builder.load_file("kv/locations.kv")
Builder.load_file("kv/settings.kv")
Builder.load_file("kv/compass.kv")
Builder.load_file("kv/prayer_times_screen.kv")
Builder.load_file("kv/calendar.kv")


class MuhasibApp(App):
	''' Muhasib app object '''
	use_kivy_settings = False
	location = ListProperty()
	icon = 'data/logo.png'

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Initialize the database
		self.database = Database()
		self.create_database_day()

		# Initializing calendar and location form to be opened
		self.calendar = Calendar()
		self.settings = Settings()
		self.compass = Compass()
		self.prayer_times_screen = PrayerTimesScreen()
		self.dashboard = Dashboard()

		# Initialize today's prayer's record
		self.dashboard.create_prayer_list()

		# Initializing the prayer times
		self.prayer_times = PrayerTimes()

		# Create interval events
		Clock.schedule_interval(self.prayer_times_screen.update_prayer_labels, 60)
		Clock.schedule_interval(self.day_pass_check, 3600)

	def on_location(self, instance, value):
		''' Change the location text and the prayer times when location is changed '''
		self.prayer_times_screen.location.text = value[0] + ", " + value[1]
		coords = self.get_geolocation()
		self.prayer_times.set_coords(coords)
		self.prayer_times.timezone = self.get_timezone(coords[0], coords[1])
		self.prayer_times_screen.update_prayer_times()
	
	def day_pass_check(self, time):
		''' Check if a day has passed and upgrade the prayer times and records if it has '''
		prayer = self.prayer_times_screen.next_prayer.text.split(":")[0]
		if self.today != date.today() and prayer != "Midnight":
			self.prayer_times_screen.update_prayer_times()
			self.dashboard.create_prayer_list()
			self.create_database_day()
		
	def create_database_day(self):
		''' Create a row in the database for the day '''
		self.today = date.today()
		self.database.create_record(self.today)

	def get_geolocation(self):
		''' Get the longitude, latitude and elevation of a place '''
		latitude, longitude, altitude = 0.0, 0.0, 0.0

		# Use the locationiq api for geocode
		try:
			url = f"https://us1.locationiq.com/v1/search.php?city={self.location[1]}&country={self.location[0]}&key=f2b114be03b247&format=json"
			response = requests.get(url).json()[0]
			latitude, longitude = response["lat"], response["lon"]

		except Exception as e:
			print("Geocode api get request failed", e)

		# Use the jawg-labs api for altitude
		try:
			url = f"https://api.jawg.io/elevations?locations={latitude},{longitude}&access-token=qKEjwRnew0P72dTdvugpdyEiz77iu9WRyB4tFlhxLHAqOZChB5nTfufUnqhZtYJh"
			altitude = requests.get(url).json()[0]["elevation"]

		except Exception as e:
			print("Altitude api get request failed", e)

		return float(latitude), float(longitude), float(altitude)

	def get_timezone(self, lat, lon):
		''' Get the timezone from longitude and latitude '''
		timezone = 0
		try:
			url = f"https://us1.unwiredlabs.com/v2/timezone.php?token=f2b114be03b247&lat={lat}&lon={lon}"
			timezone = requests.get(url).json()["timezone"]
			timezone = timezone["offset_sec"] // 3600

		except Exception as e:
			print("Timezone api get request failed", e)

		return timezone

	def get_config(self, key, defualt):
		''' Get the configuration for the specific key and return with defualt if not '''
		if key in self.settings.config.keys() and self.settings.config[key]:
			return self.settings.config[key]
		else:
			self.settings.config[key] = defualt
			return defualt

	def open_settings(self):
		''' Overriding the kivy settings screen and changing it with a complete custom system.
			This functon open the settings screen'''

		self.settings.open()

	def open_calendar(self):
		''' Open the calendar modal view '''
		self.calendar.populate()
		self.calendar.open()

	def open_compass(self):
		''' Open the compass model view '''
		self.compass.set_qibla_direction()
		self.compass.open()
	
	def open_prayer_times_screen(self):
		''' Open the prayer times model view '''
		self.prayer_times_screen.open()

	def build(self):
		return self.dashboard

if __name__ == "__main__":
	install_cache(cache_name="data/muhasib", backend="sqlite")
	MuhasibApp().run()
