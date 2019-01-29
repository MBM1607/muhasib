''' Main python file for running and defining the app object. '''

from datetime import date

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty

from prayer_times import PrayerTimes


class Dashboard(BoxLayout):
	''' Class for the main screen of the app '''

	salah_buttons_list = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.prayer_times = App.get_running_app().prayer_times
		self.update_prayer_times()
	
	# Update the prayer times
	def update_prayer_times(self):
		prayer_times = self.prayer_times.get_times(date.today(), (34.1687502, 73.2214982, 1214), 5)
		self.salah_buttons_list.data = [{"name": name.capitalize(), "time": time} for name, time in prayer_times.items()]

	

class SalahButton(BoxLayout):
	name = StringProperty()
	time = StringProperty("0:00")


class MuhasibApp(App):
	''' Muhasib app object '''
	use_kivy_settings = False

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Initializing the prayer times
		self.prayer_times = PrayerTimes()
		self.methods = {data["name"]: method for method, data in self.prayer_times.methods.items()}
	
	# Function which 
	def build_config(self, config):
		config.setdefaults("Prayer Times", {"calc_method": "Karachi", "time_format": "24h"})

	# Build the settings's panel
	def build_settings(self, settings):
		settings.add_json_panel("Prayer Times", self.config, data='''
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
				self.prayer_times.set_method(self.methods[value])
				self.root.update_prayer_times()
			elif key == "time_format":
				self.prayer_times.time_format = value
				self.root.update_prayer_times()

	def build(self):
		return Dashboard()

if __name__ == "__main__":
	MuhasibApp().run()