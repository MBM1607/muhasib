'''Module for all code related to the settings screen and storage'''

import json

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

import constants
from custom_widgets import CustomModalView, TextButton
from locations import LocationForm


RECORD_SETTINGS_DATA = [{"text": "Fasting Record", "name": "fasting_record"},
						{"text": "Quran Study Record", "name": "quran_record"},
						{"text": "Hadees Study Record", "name": "hadees_record"}]
TIMES_SETTINGS_DATA = [{"text": "Imsak Time", "name": "imsak_time"},
						{"text": "Time Format", "name": "time_format"},
						{"text": "Asr Factor", "name": "asr_factor"},
						{"text": "High Latitude Method", "name": "high_lats"},
						{"text": "Imsak Offset", "name": "imsak_offset"},
						{"text": "Dhuhr Offset", "name": "dhuhr_offset"},
						{"text": "Jummah Offset", "name": "jummah_offset"},
						{"text": "Manual Corrections", "name": "manual_times_popup_open"}]


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
									{"text": "Calendar Settings", "icon": "data/calendar.png"},
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
		popup = self.parent.parent.parent.parent
		# Special case for the manual correction setting option
		if self.text == "Manual Corrections":
			getattr(popup, self.name)()
		else:
			popup.open_setting_popup(self.name)

class PrayerTimeSettings(CustomModalView):
	'''Popup class to contain all prayer time settings'''

	def open_setting_popup(self, setting_name):
		'''Open the popup with the given setting name'''
		popup = SettingPopup(setting_name)
		popup.open()

	def manual_times_popup_open(self):
		'''Create and open the manual times adjustment popup'''
		popup = ManualTimesPopup()
		popup.open()


class ManualTimesPopup(CustomModalView):
	'''Popup class for the manual times adjustment screen'''
	
	def open_times_popup(self, name):
		'''Open the offset minutes popup'''
		popup = SettingPopup(name)
		popup.open()


class ManualTimesButton(SettingTextButton):
	'''Button for the manaul time adjustments of prayer times'''

	def on_press(self):
		'''Call the popup's function to open the times popup to select times'''
		popup = self.parent.parent.parent.parent
		popup.open_times_popup(f"{self.text.lower()}_adjustment")


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
				btn["background_color"] = constants.CAUTION_COLOR
			self.data.append(btn)

	def save_setting(self, text):
		'''Save the setting and dismiss the popup'''
		self.settings[self.name] = text
		self.dismiss()


class SettingPopupButton(TextButton):
	'''Button for the settings popup'''
	
	def on_press(self):
		'''Save the setting selected'''
		popup = self.parent.parent.parent
		popup.save_setting(self.text)


class PrayerRecordSettings(CustomModalView):
	'''Popup class for the prayer records settings'''

	def open_record_popup(self, name):
		'''Open the popup for the record which's name is passed in'''
		popup = SettingPopup(name)
		popup.open()

class RecordSettingButton(SettingTextButton):
	'''Button for the Prayer Record Settings'''
	name = StringProperty()

	def on_press(self):
		'''Open the record options popup to change record viewing setting'''
		popup = self.parent.parent.parent.parent
		popup.open_record_popup(self.name)
