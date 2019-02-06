''' Module to hold all of the various widgets used for setting and getting information about prayers '''

from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.app import App
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty


class CustomPopup(Popup):
	''' Base class for all the popups '''
	pass

class PrayerOptions(CustomPopup):
	''' Popup to be display when a prayer button is released '''
	prayer = StringProperty()
	base = ObjectProperty()

class PrayerOptionsButton(Button):
	''' Button to be used on prayer options popup'''
	base = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def on_release(self):
		popup = self.parent.parent.parent.parent
		self.base.prayer_record[popup.prayer] = self.text
		popup.dismiss()


class SalahLabel(BoxLayout):
	''' Class used to show salah name and time '''
	name = StringProperty()
	time = StringProperty("0:00")
	background_color = ListProperty((14/255, 160/255, 31/255, 1))


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
		if value == "not_prayed":
			self.background_color = (191/255, 69/255, 49/255, 1)
		elif value == "Alone":
			self.background_color = (96/255, 170/255, 37/255, 1)
		elif value == "Delayed":
			self.background_color =  (209/255, 168/255, 64/255, 1)
		elif value == "Group":
			self.background_color = (14/255, 160/255, 31/255, 1)

	def on_base(self, instance, value):
		self.prayer_options.base = self.base

class DashboardSalahButton(SalahButton):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.prayer_options.base = App.get_running_app()

class ItemsList(RecycleView):
	''' Class for various lists of items '''
	pass
