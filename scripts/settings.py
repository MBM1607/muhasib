''' Module for all code related to the settings screen and storage '''

import json

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, DictProperty, StringProperty
from kivy.clock import Clock
from kivy.app import App

from custom_widgets import CustomButton, CustomPopup, DoubleTextButton
from locations import LocationForm


class SettingsButton(DoubleTextButton):
	''' Button for settings '''
	function = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def on_press(self):
		self.function()

class Settings(Screen):
	''' Class for a settings screen to change settings '''
	settings_list = ObjectProperty()
	config = DictProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.calc_method = PrayerCalculationPopup()
		self.location_form = LocationForm()
		self.asr_factor = AsrFactorPopup()
		self.time_format = TimeFormatPopup()

		self.load_settings()

	def refresh(self):
		''' Refresh the settings data to show the current configuration '''
		self.settings_list.data = [{"name": "Prayer Calculation Method", "function": self.calc_method.open, "info": self.config["calc_method"]},
								   {"name": "Asr Factor", "function": self.asr_factor.open, "info": self.config["asr_factor"]},
								   {"name":  "Time Format", "function": self.time_format.open, "info": self.config["time_format"]},
								   {"name": "Location", "function": self.location_form.open, "info": ', '.join(self.config["location"])}]

	def open(self):
		''' Refresh and open the popup '''
		self.refresh()
		super().open()

	def load_settings(self):
		''' Load the settings from the json file and make one if it doesn't exist '''
		try:
			with open("data/settings.json", "r") as json_file:
				self.config = json.load(json_file)
				#self.location_check()
		except FileNotFoundError:
			self.config = {"location": [], "calc_method": "", "asr_factor": "", "time_format": ""}
			#self.location_check()
			self.save_settings()

		Clock.schedule_once(self.location_check)

	def location_check(self, *args):
		''' Check if location is present if not open the form to get location '''

		if self.config["location"]:
			App.get_running_app().location = self.config["location"]
		else:
			self.location_form.open()

	def save_settings(self):
		''' Save the settings in a json file '''
		with open("data/settings.json", "w") as json_file:
			json.dump(self.config, json_file)


	def on_config(self, instance, value):
		''' When config changes then upgrade prayer times and save the settings '''
		app = App.get_running_app()
		if hasattr(app, "prayer_times_screen"):
			app.prayer_times_screen.update_prayer_times()
		self.refresh()
		self.save_settings()


class SettingsPopup(CustomPopup):
	''' Base Class for the settings popup '''
	recycle_view = ObjectProperty()
	config_name = StringProperty()


class PrayerCalculationPopup(SettingsPopup):
	''' Popup to select the prayer calculation method '''
	def open(self):
		''' open the popup and fill it with options '''
		methods = App.get_running_app().prayer_times.methods
		self.recycle_view.data = [{"text": method} for method in methods.keys()]
		super().open()


class AsrFactorPopup(SettingsPopup):
	''' Popup to choose asr factor '''
	def open(self):
		''' open the popup and fill it with options '''
		self.recycle_view.data = [{"text": "Standard"}, {"text": "Hanafi"}]
		super().open()

class TimeFormatPopup(SettingsPopup):
	''' Popup to choose the asr factor '''
	def open(self):
		''' open the popup and fill it with options '''
		self.recycle_view.data = [{"text": "12h"}, {"text": "24h"}]
		super().open()


class SettingsPopupButton(CustomButton):
	''' Button for Settings Popup '''
	def on_press(self):
		settings = App.get_running_app().settings
		config = settings.config
		popup = self.parent.parent.parent.parent.parent
		config[popup.config_name] = self.text

		popup.dismiss()
