''' Module to hold all of the various widgets used for setting and getting information about prayers '''

from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.button import ButtonBehavior

import constants
from custom_widgets import CustomButton, CustomPopup, DoubleTextButton


class PrayerOptions(CustomPopup):
	''' Popup to be display when a prayer button is released '''
	prayer = StringProperty()
	base = ObjectProperty()

	def __init__(self, prayer="", base=None, **kwargs):
		super().__init__(*kwargs)
		self.prayer = prayer.lower()
		self.base = base


class PrayerOptionsButton(CustomButton):
	''' Button to be used on prayer options popup'''

	def on_release(self):
		''' Change the prayer record according to the button pressed '''
		popup = self.parent.parent.parent.parent
		popup.base.update_prayer_record(popup.prayer, self.text)
		popup.dismiss()


class SalahButton(DoubleTextButton):
	''' Button used with salah button on home screen with popup functionality'''
	base = ObjectProperty()

	def on_release(self):
		''' On button release open the popup '''
		self.base.open_prayer_options(self.name)

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


class RecordLists(BoxLayout):
	''' Class for the layout of Record Items List '''
	salah_record_list = ObjectProperty()
	extra_record_list = ObjectProperty()

	def create_lists(self, base, prayer_record, extra_record):
		''' Create and populate the record lists from the record provided '''
		self.salah_record_list.data = [{"name": n.capitalize(), "info": r, "base": base} for n, r in prayer_record.items()]
		self.extra_record_list.data = [{"name": n.capitalize(), "active": r, "base": base} for n, r in extra_record.items()]

	def update_prayer_record(self, prayer, record):
		''' Change the prayer record for the provided prayer '''
		for child in self.salah_record_list.children[0].children:
			if child.name.lower() == prayer:
				child.info = record