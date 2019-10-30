''' Module for all code relating to the determining the qibla direction '''

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class Compass(Screen):
	''' Class for the screen containing compass '''
	qibla_direction = StringProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.bind(on_pre_enter=lambda _: self.set_qibla_direction())
		self.bind(on_leave=lambda _: self.remove_qibla_direction())

	def remove_qibla_direction(self):
		''' Remove the qibla direction '''
		self.qibla_direction = ""

	def set_qibla_direction(self):
		''' Set the qibla direction from current position '''

		qibla_direction = self.app.prayer_times.get_qibla()

		if qibla_direction < 0:
			self.qibla_direction = f"{abs(qibla_direction)} from North towards West"
		else:
			self.qibla_direction = f"{qibla_direction} from North towards East"
