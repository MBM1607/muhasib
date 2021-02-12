'''Module for all code related to the settings screen and storage'''

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty

import constants
from custom_widgets import (CustomModalView, CustomScreen,
							HorizontalIconTextButton, TextButton)

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

MANUAL_TIMES_DATA = [{"text": text, "name": f"{text.lower()}_adjustment"} for text in constants.PRAYER_NAMES]

SETTING_NAME_DATA = {"Calendar Settings": CALENDAR_SETTINGS_DATA,
					 "Prayer Record Settings": RECORD_SETTINGS_DATA,
					 "Prayer Time Settings": TIMES_SETTINGS_DATA,
					 "Notification Settings": [],
					 "Manual Time Adjustments": MANUAL_TIMES_DATA}


class SettingsScreen(CustomScreen):
	'''Class for a settings screen to change settings'''
	settings_list = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.bind(on_pre_enter=lambda _: self.create_settings_list())
		self.bind(on_leave=lambda _: self.destroy_settings_list())

	def create_settings_list(self):
		'''Create the settings list and the required popups'''
		self.settings_list.data = [
									{"text": "Prayer Time Settings", "icon": "data/time.png"},
									{"text": "Prayer Record Settings", "icon": "data/record.png"},
									{"text": "Calendar Settings", "icon": "data/calendar.png"},
									{"text": "Notification Settings", "icon": "data/notification.png"}
								]

	def destroy_settings_list(self):
		'''Destroy the settings list'''
		self.settings_list.data = []


class SettingListButton(HorizontalIconTextButton):
	'''Button for the setting screens list'''

	def on_press(self):
		'''Open the settings popup'''
		SettingsPopup(self.text).open()


class SettingTextButton(TextButton):
	'''TextButton for use on Setting's popups'''
	pass


class SettingsPopup(CustomModalView):
	'''Popup class for various settings screens'''
	name = StringProperty()
	data = ListProperty()

	def __init__(self, name='', **kwargs):
		super().__init__(**kwargs)
		self.name = name
		self.data = SETTING_NAME_DATA[name]


class OptionsPopup(CustomModalView):
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


class OptionsPopupButton(SettingTextButton):
	'''Base Button for a single settings in any kind of settings popup'''
	name = StringProperty()

	def on_press(self):
		'''Open the settings options popup'''
		if self.text == "Manual Corrections":
			SettingsPopup("Manual Time Adjustments").open()
		else:
			OptionsPopup(self.name).open()


class PopupOptionButton(TextButton):
	'''Button for the settings popup options'''

	def on_press(self):
		'''Save the setting selected'''
		popup = self.parent.parent.parent.parent
		popup.save_setting(self.text)
