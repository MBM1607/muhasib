''' Module for all code related to the settings screen and storage '''

import json

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

import constants
from custom_widgets import (CustomModalView, HorizontalIconTextButton,
							TextButton)
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

	def open_popup(self, setting_name):
		''' Open the popup with the given setting name '''
		popup = SettingsPopup(setting_name)
		popup.open()


class SettingsPopup(CustomModalView):
	''' Popup class for all the setting options '''
	data = ListProperty()

	def __init__(self, setting_name, **kwargs):
		super().__init__(**kwargs)
		self.settings = App.get_running_app().settings
		self.name = setting_name

		self.bind(on_pre_open=lambda _: self.create_data_list())

	def create_data_list(self):
		''' Create the data list for the chosen settings '''
		for text in constants.SETTINGS_OPTIONS[self.name]:
			btn = {"text": text}
			if text == self.settings[self.name]:
				btn["background_color"] = constants.SECONDRY_COLOR
			else:
				btn["background_color"] = constants.CAUTION_COLOR
			self.data.append(btn)

	def save_setting(self, text):
		''' Save the setting and dismiss the popup '''
		self.settings[self.name] = text
		self.dismiss()


class SettingPopupButton(TextButton):
	''' Button for the settings popup '''
	
	def on_press(self):
		popup = self.parent.parent.parent
		popup.save_setting(self.text)