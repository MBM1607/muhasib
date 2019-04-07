''' Module to hold all of the various widgets used for setting and getting information about prayers '''

from kivy.uix.behaviors.button import ButtonBehavior
from kivy.app import App
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

from custom_widgets import CustomPopup, CustomButton, DoubleTextButton


class PrayerOptions(CustomPopup):
	''' Popup to be display when a prayer button is released '''
	prayer = StringProperty()
	base = ObjectProperty()

class PrayerOptionsButton(CustomButton):
	''' Button to be used on prayer options popup'''

	def on_release(self):
		popup = self.parent.parent.parent.parent
		popup.base.prayer_record[popup.prayer] = self.text
		popup.dismiss()


class SalahButton(DoubleTextButton):
	''' Button used with salah button on home screen with popup functionality'''

	record = StringProperty()
	base = ObjectProperty()
	editable = BooleanProperty()

	def __init__(self, **kwargs):
		super(SalahButton, self).__init__(**kwargs)
		self.prayer_options = PrayerOptions()

	def on_release(self):
		''' On button release open the popup '''
		if self.editable:
			self.prayer_options.prayer = self.name.lower()
			self.prayer_options.open()

	def on_record(self, instance, value):
		''' React to prayer record changing '''
		if value == "Not prayed":
			self.background_color = (161/255, 39/255, 19/255, 1)
		elif value == "Alone":
			self.background_color = (46/255, 130/255, 0, 1)
		elif value == "Delayed":
			self.background_color =  (169/255, 128/255, 24/255, 1)
		elif value == "Group":
			self.background_color = (26/255, 102/255, 38/255, 1)

	def on_base(self, instance, value):
		self.prayer_options.base = self.base

class DashboardSalahButton(SalahButton):
	def __init__(self, **kwargs):
		super(DashboardSalahButton, self).__init__(**kwargs)
		self.prayer_options.base = App.get_running_app()
