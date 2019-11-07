''' Module for all code related to the settings screen and storage '''

import json

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App

from custom_widgets import HorizontalIconTextButton, CustomModalView, TextButton
from locations import LocationForm

class SettingsButton(HorizontalIconTextButton):
	''' Settings button class for the opening different setting popups '''
	pass


class SettingTextButton(TextButton):
	''' TextButton for use on Setting's popups '''
	pass


class SettingsScreen(Screen):
	''' Class for a settings screen to change settings '''
	settings_list = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.bind(on_pre_enter=lambda _: self.create_settings_list())
		self.bind(on_leave=lambda _: self.destroy_settings_list())
	
	def create_settings_list(self):
		''' Create the settings list and the required popups '''
		self.settings_list.data = [
									{"text": "Prayer Times Settings", "icon": "data/time.png", "on_press": PrayerTimeSettings().open},
									{"text": "Prayer Record Settings", "icon": "data/record.png"},
									{"text": "Calendar Settings", "icon": "data/calendar.png"},
									{"text": "Location Settings", "icon": "data/location.png", "on_press": LocationForm().open},
									{"text": "Notifications Settings", "icon": "data/notification.png"}
								]

	def destroy_settings_list(self):
		''' Destroy the settings list '''
		self.settings_list.data = []


class PrayerTimeSettings(CustomModalView):
	''' Popup class to contain all prayer time settings '''
	def __init__(self, **kwargs):
		super().__init__(**kwargs)