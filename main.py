''' Main python file for running and defining the app object. '''

from datetime import date
import time
import requests
from requests_cache import install_cache

from kivy.app import App
from kivy.properties import DictProperty
from kivy.lang.builder import Builder

from scripts.prayer_times import PrayerTimes
from scripts.calendar import Calendar
from scripts.database import Database
from scripts.dashboard import Dashboard


Builder.load_file("scripts/dashboard.kv")
Builder.load_file("scripts/prayer_widgets.kv")
Builder.load_file("scripts/calendar.kv")

class MuhasibApp(App):
	''' Muhasib app object '''
	use_kivy_settings = False
	prayer_record = DictProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Get the current location by prompting the user
		self.location = "Haripur Khyber Pakhtunkhwa Pakistan"

		# get today's date
		self.today = date.today()

		# Initialize the database
		self.database = Database()
		self.database.create_prayer_record(self.today)

		prayer_record = self.database.get_prayer_record(self.today)

		# Initialize today's prayer's record
		self.prayer_record = {"fajr": prayer_record[2], "dhuhr": prayer_record[3], "asr": prayer_record[4],
							"maghrib": prayer_record[5], "isha": prayer_record[6]}

		# https://stackoverflow.com/a/10854983/9159700
		timezone = time.timezone if time.localtime().tm_isdst == 0 else time.altzone
		timezone /= 3600 * -1

		# Initializing the prayer times
		coords = self.get_geolocation()
		self.prayer_times = PrayerTimes(timezone=timezone, coords=coords)
		self.methods = {data["name"]: method for method, data in self.prayer_times.methods.items()}

		self.calendar = Calendar()

	# Set the location on all classes
	def set_location(self, location):
		self.location = location
		self.root.location.text = location

	# On change of prayer_record store it on the drive
	def on_prayer_record(self, instance, value):
		# If their is a window then update the dashboard button's color
		if self.root:
			self.root.update_salah_buttons_record()
		self.database.update_prayer_record(self.today, **self.prayer_record)
		
	# Get the longitude, latitude and elevation of a place
	def get_geolocation(self):
		latitude, longitude, altitude = 0.0, 0.0, 0.0

		# Use the locationiq api for geocode
		try:
			url = f"https://us1.locationiq.com/v1/search.php?q={self.location}&key=f2b114be03b247&format=json"
			response = requests.get(url).json()[0]
			latitude, longitude = response["lat"], response["lon"]

		except Exception as e:
			print("loctioniq api get request failed", e)

		# Use the jawg-labs api for altitude
		try:
			url = f"https://api.jawg.io/elevations?locations={latitude},{longitude}&access-token=qKEjwRnew0P72dTdvugpdyEiz77iu9WRyB4tFlhxLHAqOZChB5nTfufUnqhZtYJh"
			altitude = requests.get(url).json()[0]["elevation"]

		except Exception as e:
			print("jawg-labs api get request failed", e)

		return float(latitude), float(longitude), float(altitude)

	# Create configuration file
	def build_config(self, config):
		config.setdefaults("Prayer Times", {"calc_method": "Karachi", "time_format": "24h"})

	# Build the settings's panel
	def build_settings(self, settings):
		settings.add_json_panel("Prayer Times Setting", self.config, data='''
			[
				{"type": "options",
				"title": "Calculation method",
				"section": "Prayer Times",
				"key": "calc_method",
				"options": ["Muslim World League", "Islamic Society of North America (ISNA)", "Egyptian General Authority of Survey",
							"Umm Al-Qura University, Makkah", "University of Islamic Sciences, Karachi", "Institute of Geophysics, University of Tehran",
							"Shia Ithna-Ashari, Leva Institute, Qum"]
				},
				{"type": "options",
				"title": "Time Format",
				"section": "Prayer Times",
				"key": "time_format",
				"options": ["24h", "12h"]
				}
			]'''
			)

	# React when configuration is changed in settings
	def on_config_change(self, config, section, key, value):
		if section == "Prayer Times":
			if key == "calc_method":
				self.root.update_prayer_times()
			elif key == "time_format":
				self.root.update_prayer_times()

	# Open the calendar modal view
	def open_calendar(self):
		self.calendar.open()

	def build(self):
		return Dashboard()

if __name__ == "__main__":
	install_cache(cache_name="muhasib", backend="sqlite")
	MuhasibApp().run()