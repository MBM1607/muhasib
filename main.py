''' Main python file for running and defining the app object. '''

from datetime import date
import requests
from requests_cache import install_cache
import json

from kivy.app import App
from kivy.properties import DictProperty, ListProperty
from kivy.clock import Clock
from kivy.lang.builder import Builder

from scripts.prayer_times import PrayerTimes
from scripts.calendar import Calendar
from scripts.database import Database
from scripts.dashboard import Dashboard
from scripts.settings import Settings


Builder.load_file("scripts/dashboard.kv")
Builder.load_file("scripts/prayer_widgets.kv")
Builder.load_file("scripts/locations.kv")
Builder.load_file("scripts/settings.kv")

class MuhasibApp(App):
	''' Muhasib app object '''

	use_kivy_settings = False
	prayer_record = DictProperty()
	location = ListProperty()
	icon = 'data/logo.png'

	def __init__(self, **kwargs):
		super(MuhasibApp, self).__init__(**kwargs)

		# get today's date
		self.today = date.today()

		# Initialize the database
		self.database = Database()
		self.database.create_prayer_record(self.today)

		prayer_record = self.database.get_prayer_record(self.today)

		# Initialize today's prayer's record
		self.prayer_record = {"fajr": prayer_record[2], "dhuhr": prayer_record[3], "asr": prayer_record[4],
							"maghrib": prayer_record[5], "isha": prayer_record[6]}

		# Initializing calendar and location form to be opened
		self.calendar = Calendar()
		self.settings = Settings()

		# Initializing the prayer times
		self.prayer_times = PrayerTimes()
		self.methods = {data["name"]: method for method, data in self.prayer_times.methods.items()}

	def on_location(self, instance, value):
		''' Change the location text when location is changed '''
		self.root.location.text = value[0] + ", " + value[1]
		coords = self.get_geolocation()
		self.prayer_times.set_coords(coords)
		self.prayer_times.timezone = self.get_timezone(coords[0], coords[1])
		self.root.update_prayer_times()

	def on_prayer_record(self, instance, value):
		''' On change of prayer_record store it on the drive '''

		# If their is a window then update the dashboard button's color
		if self.root:
			self.root.update_salah_buttons_record()
		self.database.update_prayer_record(self.today, **self.prayer_record)

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

	def build(self):
		return Dashboard()

if __name__ == "__main__":
	install_cache(cache_name="muhasib", backend="sqlite")
	MuhasibApp().run()
