''' Main python file for running and defining the app object. '''

from datetime import date
import time
import requests

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty

from prayer_times import PrayerTimes


class Dashboard(BoxLayout):
	''' Class for the main screen of the app '''

	salah_list = ObjectProperty()
	current_prayer = ObjectProperty()
	prayer_time_left = ObjectProperty()
	location = ObjectProperty()


	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
		self.app = App.get_running_app()
		self.location.text = self.app.location
		self.prayer_times = self.app.prayer_times
		self.update_prayer_times()
	
	# Update the prayer times
	def update_prayer_times(self, time_format="", calc_method=""):
		if not time_format:
			time_format = self.app.config.getdefault("Prayer Times", "time_format", "24h")
		if not calc_method:
			calc_method = self.app.config.getdefault("Prayer Times", "calc_method", "Karachi")

		self.prayer_times.time_format = time_format
		self.prayer_times.set_method(self.app.methods[calc_method])
		prayer_times = self.prayer_times.get_times(date.today())
		self.salah_list.data = [{"name": name.capitalize(), "time": time} for name, time in prayer_times.items()]

	

class SalahLabel(BoxLayout):
	name = StringProperty()
	time = StringProperty("0:00")


class MuhasibApp(App):
	''' Muhasib app object '''
	use_kivy_settings = False

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Get the current location by prompting the user
		self.location = "Haripur Khyber Pakhtunkhwa Pakistan"

		# https://stackoverflow.com/a/10854983/9159700
		timezone = time.timezone if time.localtime().tm_isdst == 0 else time.altzone
		timezone /= 3600 * -1

		# Initializing the prayer times
		coords = self.get_geolocation(self.location)
		self.prayer_times = PrayerTimes(timezone=timezone, coords=coords)
		self.methods = {data["name"]: method for method, data in self.prayer_times.methods.items()}
	
	# Get the longitude, latitude and elevation of a place
	def get_geolocation(self, place):
		latitude, longitude, altitude = 0.0, 0.0, 0.0

		# Use the locationiq api for geocode
		try:
			params = {"key": "f2b114be03b247", "q": place, "format": "json"}
			response = requests.get("https://us1.locationiq.com/v1/search.php", params=params).json()[0]
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
				self.root.update_prayer_times(calc_method=value)
			elif key == "time_format":
				self.root.update_prayer_times(time_format=value)

	def build(self):
		return Dashboard()

if __name__ == "__main__":
	MuhasibApp().run()