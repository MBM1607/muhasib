'''Module for all code relating to the determining the qibla direction'''

from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty

from custom_widgets import CustomScreen


class QiblaScreen(CustomScreen):
	'''Class for the screen containing compass'''
	needle_angle = NumericProperty(0)
	location_text = StringProperty()
	title = StringProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.bind(on_pre_enter=lambda _: self.set_qibla_direction())
		self.bind(on_leave=lambda _: self.remove_qibla_direction())

	def refresh(self):
		'''Refresh the screen'''
		self.set_qibla_direction()

	def remove_qibla_direction(self):
		'''Remove the qibla direction'''
		self.needle_angle = 0
		self.location_text = ""

	def set_qibla_direction(self):
		'''Set the qibla direction from current position'''

		self.location_text = self.app.settings["location"]
		qibla_direction = self.app.prayer_times.get_qibla()
		self.needle_angle = (360 - qibla_direction) % 360
		self.title = f"Qibla ({self.needle_angle}°)"
