'''Module for all code related to the settings screen and storage'''

import json

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

import constants
from custom_widgets import CustomModalView, TextButton
from locations import LocationForm

CALENDAR_SETTINGS_DATA = [{"text": "Hijri Adjustment", "name": "hijri_adjustment"}]

RECORD_SETTINGS_DATA = [{"text": "Fasting Record", "name": "fasting_record"},
						{"text": "Quran Study Record", "name": "quran_record"},
						{"text": "Hadees Study Record", "name": "hadees_record"}]

TIMES_SETTINGS_DATA = [{"text": "Imsak Time", "name": "imsak_time"},
						{"text": "Prayer Calculation Method", "name": "calc_method"},
						{"text": "Time Format", "name": "time_format"},
						{"text": "Asr Factor", "name": "asr_factor"},
						{"text": "High Latitude Method", "name": "high_lats"},
						{"text": "Imsak Offset", "name": "imsak_offset"},
						{"text": "Dhuhr Offset", "name": "dhuhr_offset"},
						{"text": "Jummah Offset", "name": "jummah_offset"},
						{"text": "Manual Corrections"}]


class SettingTextButton(TextButton):
	'''TextButton for use on Setting's popups'''
	pass


class SettingsScreen(Screen):
	'''Class for a settings screen to change settings'''
	settings_list = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.bind(on_pre_enter=lambda _: self.create_settings_list())
		self.bind(on_leave=lambda _: self.destroy_settings_list())
	
	def create_settings_list(self):
		'''Create the settings list and the required popups'''
		self.settings_list.data = [
									{"text": "Prayer Times Settings", "icon": "data/time.png", "on_press": PrayerTimeSettings().open},
									{"text": "Prayer Record Settings", "icon": "data/record.png", "on_press": PrayerRecordSettings().open},
									{"text": "Calendar Settings", "icon": "data/calendar.png", "on_press": CalendarSettings().open},
									{"text": "Location Settings", "icon": "data/location.png", "on_press": LocationForm().open},
									{"text": "Notifications Settings", "icon": "data/notification.png"}
								]

	def destroy_settings_list(self):
		'''Destroy the settings list'''
		self.settings_list.data = []


class PrayerSettingButton(SettingTextButton):
	'''Button for the prayer times settings'''
	name = StringProperty()

	def on_press(self):
		'''Open the setting popup'''
		# Special case for the manual correction setting option
		if self.text == "Manual Corrections":
			ManualTimesPopup().open()
		else:
			open_settings_popup(self.name)


class CalendarSettings(CustomModalView):
	'''Popup class for calendar settings'''
	pass


class PrayerRecordSettings(CustomModalView):
	'''Popup class for the prayer records settings'''
	pass


class ManualTimesPopup(CustomModalView):
	'''Popup class for the manual times adjustment screen'''
	pass


class PrayerTimeSettings(CustomModalView):
	'''Popup class to contain all prayer time settings'''
	pass


class SettingPopup(CustomModalView):
	'''Popup class for all the setting options'''
	data = ListProperty()

	def __init__(self, setting_name, **kwargs):
		super().__init__(**kwargs)
		self.settings = App.get_running_app().settings
		self.name = setting_name

		self.bind(on_pre_open=lambda _: self.create_data_list())

	def create_data_list(self):
		'''Create the data list for the chosen settings'''
		for text in constants.SETTINGS_OPTIONS[self.name]:
			btn = {"text": text}
			if text == self.settings[self.name]:
				btn["background_color"] = constants.SECONDRY_COLOR
			else:
				btn["background_color"] = constants.WARNING_COLOR
			self.data.append(btn)

	def save_setting(self, text):
		'''Save the setting and dismiss the popup'''
		self.settings[self.name] = text
		self.dismiss()


class SettingPopupButton(SettingTextButton):
	'''Base Button for a single settings in any kind of settings popup'''
	name = StringProperty()

	def on_press(self):
		'''Open the settings options popup'''
		open_settings_popup(self.name)


class PopupOptionButton(TextButton):
	'''Button for the settings popup options'''
	
	def on_press(self):
		'''Save the setting selected'''
		popup = self.parent.parent.parent.parent
		popup.save_setting(self.text)


def open_settings_popup(settings_name):
	'''Open the settings popup with the setting name'''
	SettingPopup(settings_name).open()
