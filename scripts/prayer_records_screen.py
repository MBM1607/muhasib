''' Module to hold the prayer record screen class '''

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen


class PrayerRecordsScreen(Screen):
	''' Screen to show today's record list '''

	record_lists = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.bind(on_pre_enter=lambda _: self.record_lists.create_lists())
		self.bind(on_leave=lambda _: self.record_lists.destroy_lists())

