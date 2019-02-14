''' Module to hold all of the various widgets used for setting and getting information about prayers '''

from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

from custom_widgets import CustomPopup, CustomButton


class PrayerOptions(CustomPopup):
	''' Popup to be display when a prayer button is released '''
	prayer = StringProperty()
	base = ObjectProperty()

class PrayerOptionsButton(CustomButton):
	''' Button to be used on prayer options popup'''

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def on_release(self):
		popup = self.parent.parent
		popup.base.prayer_record[popup.prayer] = self.text
		popup.dismiss()


class SalahLabel(BoxLayout):
	''' Class used to show salah name and time '''
	name = StringProperty()
	time = StringProperty("0:00")
	background_colors = ListProperty(((5, 55, 11, 230), (2, 40, 14, 255)))


class SalahButton(ButtonBehavior, SalahLabel):
	''' Button used with salah button on home screen with popup functionality'''

	record = StringProperty()
	base = ObjectProperty()
	editable = BooleanProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.prayer_options = PrayerOptions()

	def on_release(self):
		''' On button release open the popup '''
		if self.editable:
			self.prayer_options.prayer = self.name.lower()
			self.prayer_options.open()

	def on_record(self, instance, value):
		''' React to prayer record changing '''
		if value == "Not prayed":
			self.background_colors = ((191, 69, 49, 220), (161, 39, 19, 255))
		elif value == "Alone":
			self.background_colors = ((96, 170, 37, 220), (46, 130, 0, 255))
		elif value == "Delayed":
			self.background_colors =  ((209, 168, 64, 220), (169, 128, 24, 255))
		elif value == "Group":
			self.background_colors = ((14, 160, 31, 220), (0, 120, 0, 255))

	def on_base(self, instance, value):
		self.prayer_options.base = self.base

class DashboardSalahButton(SalahButton):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.prayer_options.base = App.get_running_app()
