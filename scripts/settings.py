''' Module for all code related to the settings screen and storage '''

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.app import App

from custom_widgets import CustomModalView, CustomButton


class SettingsButton(CustomButton):
	''' Button for settings '''

	def __init__(self, **kwargs):
		super(SettingsButton, self).__init__(**kwargs)

	def on_press(self, *args):
		functions = App.get_running_app().functions
		functions[self.text]()

class Settings(CustomModalView):
	''' Class for a settings screen to change settings '''

	settings_list = ObjectProperty()

	def __init__(self, **kwargs):
		super(Settings, self).__init__(**kwargs)
		
		self.settings_list.data = [{"text": t} for t in ["Prayer Calculation Method", "Asr Factor", "Time Format", "Location"]]
