''' Module for all code related to the settings screen and storage '''

import json
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, DictProperty, StringProperty
from kivy.app import App

from custom_widgets import CustomModalView, CustomButton, CustomPopup, DoubleTextButton
from locations import LocationForm


class SettingsButton(DoubleTextButton):
	''' Button for settings '''
	function = ObjectProperty()

	def __init__(self, **kwargs):
		super(SettingsButton, self).__init__(**kwargs)

	def on_press(self):
		self.function()

class Settings(CustomModalView):
	''' Class for a settings screen to change settings '''

	settings_list = ObjectProperty()
	config = DictProperty()

	def __init__(self, **kwargs):
		super(Settings, self).__init__(**kwargs)
		self.calc_method = PrayerCalculationPopup()
		self.location_form = LocationForm()
		self.asr_factor = AsrFactorPopup()
		self.time_format = TimeFormatPopup()
		
		self.load_settings()

	
	def refresh(self):
		self.settings_list.data = [{"name": "Prayer Calculation Method", "function": self.calc_method.open, "info": self.config["calc_method"]},
								   {"name": "Asr Factor", "function": self.asr_factor.open, "info": self.config["asr_factor"]},
								   {"name":  "Time Format", "function": self.time_format.open, "info": self.config["time_format"]},
								   {"name": "Location", "function": self.location_form.open, "info": ', '.join(self.config["location"])}]

	def open(self):
		self.refresh()

		super(Settings, self).open()

	def load_settings(self):
		try:
			with open("data/settings.json", "r") as json_file:
				self.config = json.load(json_file)
				#self.location_check()
		except FileNotFoundError:
			self.config = {"location": [], "calc_method": "", "asr_factor": "", "time_format": ""}
			#self.location_check()
			self.save_settings()
		
		from kivy.clock import Clock
		Clock.schedule_once(self.location_check)

	def location_check(self, *args):
		''' Check if location is present if not open the form to get location '''
		if self.config["location"]:
			App.get_running_app().location = self.config["location"]
		else:
			self.location_form.open()

	def save_settings(self):
		with open("data/settings.json", "w") as json_file:
			json.dump(self.config, json_file)

	
	def on_config(self, instance, value):
		root = App.get_running_app().root
		if root:
			root.update_prayer_times()
		self.refresh()
		self.save_settings()

class SettingsPopup(CustomPopup):
	recycle_view = ObjectProperty()
	config_name = StringProperty()

class PrayerCalculationPopup(SettingsPopup):
	def open(self):
		methods = App.get_running_app().methods
		self.recycle_view.data = [{"text": method} for method in methods.keys()]
		super(PrayerCalculationPopup, self).open()

class AsrFactorPopup(SettingsPopup):
	def open(self):
		self.recycle_view.data = [{"text": "Standard"}, {"text": "Hanafi"}]
		super(AsrFactorPopup, self).open()

class TimeFormatPopup(SettingsPopup):
	def open(self):
		self.recycle_view.data = [{"text": "12h"}, {"text": "24h"}]
		super(TimeFormatPopup, self).open()
	

class PrayerCalculationButton(CustomButton):

	def on_press(self):
		settings = App.get_running_app().settings
		config = settings.config
		popup = self.parent.parent.parent.parent.parent
		config[popup.config_name] = self.text

		popup.dismiss()

