''' Main python file for running and defining the app object. '''

from datetime import datetime, date, timedelta
import time
import requests

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, ListProperty

from scripts.prayer_times import PrayerTimes
from scripts.calendar import Calendar


class PrayerOptions(Popup):
	''' Popup to be display when a prayer button is released '''
	prayer = StringProperty()

class PrayerOptionsButton(Button):
	''' Button to be used on prayer options popup'''

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()

	def on_release(self):
		popup = self.parent.parent.parent.parent
		self.app.prayer_record[popup.prayer] = self.text
		print(self.app.prayer_record)
		popup.dismiss()

class Dashboard(BoxLayout):
	''' Class for the main screen of the app '''

	times_list = ObjectProperty()
	salah_list = ObjectProperty()
	current_prayer = ObjectProperty()
	prayer_time_left = ObjectProperty()
	next_prayer = ObjectProperty()
	location = ObjectProperty()


	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
		self.app = App.get_running_app()
		self.location.text = self.app.location
		self.update_prayer_times()
	
	# Update the prayer times
	def update_prayer_times(self, time_format="", calc_method=""):
		if not time_format:
			time_format = self.app.config.getdefault("Prayer Times", "time_format", "24h")
		if not calc_method:
			calc_method = self.app.config.getdefault("Prayer Times", "calc_method", "Karachi")

		self.app.prayer_times.time_format = time_format
		self.app.prayer_times.set_method(self.app.methods[calc_method])
		prayer_data = self.app.prayer_times.get_times(date.today())
		self.update_prayer_labels(prayer_data)
		self.times_list.data = [{"name": n.capitalize(), "time": t} for n, t in prayer_data.items()]
		self.salah_list.data = [{"name": n.capitalize(), "time": t} for n, t in prayer_data.items() if n in ["fajr", "dhuhr", "asr", "maghrib", "isha"]]

	# Change the labels reporting information about prayers
	def update_prayer_labels(self, prayer_data):

		current_time = datetime.strptime(datetime.strftime(datetime.now(), "%H:%M"), "%H:%M")
		time_left = timedelta(24)
		current_prayer = ""
		next_prayer = ""
		prayer_names = list(prayer_data.keys())
		prayer_index = 0

		for n, t in prayer_data.items():
			if self.app.prayer_times.time_format == "12h":
				t = datetime.strptime(t, "%I:%M %p")
				if t < current_time:
					t += timedelta(1)

			dt = t - current_time
			if dt < time_left:
				time_left = dt
				current_prayer = prayer_names[prayer_index-1]
				next_prayer = n

			prayer_index += 1

		self.prayer_time_left.text = (datetime.min + time_left).time().strftime("%H:%M")	
		self.current_prayer.text = current_prayer.capitalize()
		self.next_prayer.text = next_prayer.capitalize()

class SalahLabel(BoxLayout):
	''' Class used to show salah name and time '''
	name = StringProperty()
	time = StringProperty("0:00")
	background_color = ListProperty((14/255, 160/255, 31/255, 1))

class SalahButton(ButtonBehavior, SalahLabel):
	''' Button used with salah button on home screen with popup functionality'''

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.prayer_options = PrayerOptions()

	# On button release open the popup
	def on_release(self):
		self.prayer_options.prayer = self.name.lower()
		self.prayer_options.open()


class MuhasibApp(App):
	''' Muhasib app object '''
	use_kivy_settings = False

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Initialize today's prayer's record
		self.prayer_record = {"fajr": "not_prayed", "dhuhr": "not_prayed", "asr": "not_prayed",
							"maghrib": "not_prayed", "isha": "not_prayed"}

		# Get the current location by prompting the user
		self.location = "Haripur Khyber Pakhtunkhwa Pakistan"

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
				self.root.update_prayer_times(calc_method=value)
			elif key == "time_format":
				self.root.update_prayer_times(time_format=value)

	# Open the calendar modal view
	def open_calendar(self):
		self.calendar.open()

	def build(self):
		return Dashboard()

if __name__ == "__main__":
	MuhasibApp().run()