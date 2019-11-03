''' Module for all code related to the settings screen and storage '''

import json

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App

from custom_widgets import TextButton, CustomModalView, DoubleTextButton
from locations import LocationForm


class SettingsButton(DoubleTextButton):
	''' Button for settings '''
	function = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def on_press(self):
		self.function()

class SettingsScreen(Screen):
	''' Class for a settings screen to change settings '''
	settings_list = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.bind(on_pre_enter=lambda _: self.create_settings_list())
		self.bind(on_pre_leave=lambda _: self.destroy_settings_list())
	
	def create_settings_list(self):
		''' Create the settings list and the required popups '''
		settings = App.get_running_app().settings
		self.calc_method = PrayerCalculationPopup()
		self.asr_factor = AsrFactorPopup()
		self.time_format = TimeFormatPopup()
		self.location_form = LocationForm()
		self.settings_list.data = [
									{"name": "Prayer Calculation Method", "function": self.calc_method.open, "info": settings["calc_method"]},
									{"name": "Asr Factor", "function": self.asr_factor.open, "info": settings["asr_factor"]},
									{"name":  "Time Format", "function": self.time_format.open, "info": settings["time_format"]},
									{"name": "Location", "function": self.location_form.open, "info": settings["location"]}
								]

	def destroy_settings_list(self):
		''' Destroy the settings list '''
		self.calc_method = None
		self.asr_factor = None
		self.time_format = None
		self.settings_list.data = []


class SettingsPopup(CustomModalView):
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


class SettingsPopupButton(TextButton):
	''' Button for Settings Popup '''
	def on_press(self):
		''' Change the configuration to the chosen button's text '''
		settings = App.get_running_app().settings
		popup = self.parent.parent.parent
		settings[popup.config_name] = self.text

		popup.dismiss()
