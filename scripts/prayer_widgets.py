''' Module to hold all of the various widgets used for setting and getting information about prayers '''

from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors.button import ButtonBehavior

import constants
from custom_widgets import CustomButton, CustomPopup, DoubleTextButton


class PrayerOptions(CustomPopup):
	''' Popup to be display when a prayer button is released '''
	prayer = StringProperty()
	base = ObjectProperty()


class PrayerOptionsButton(CustomButton):
	''' Button to be used on prayer options popup'''

	def on_release(self):
		''' Change the prayer record according to the button pressed '''
		popup = self.parent.parent.parent.parent
		popup.base.prayer_record[popup.prayer] = self.text
		popup.dismiss()


class SalahButton(DoubleTextButton):
	''' Button used with salah button on home screen with popup functionality'''

	base = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.prayer_options = PrayerOptions()

	def on_release(self):
		''' On button release open the popup '''
		self.prayer_options.prayer = self.name.lower()
		self.prayer_options.open()

	def on_info(self, instance, value):
		''' React to prayer record changing '''
		if value == "Not prayed":
			self.background_color = constants.WARNING_COLOR
		elif value == "Alone":
			self.background_color = constants.TERNARY_COLOR
		elif value == "Delayed":
			self.background_color =  constants.CAUTION_COLOR
		elif value == "Group":
			self.background_color = constants.SECONDRY_COLOR

	def on_base(self, instance, value):
		self.prayer_options.base = self.base


class DashboardSalahButton(SalahButton):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
