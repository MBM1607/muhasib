''' Module to hold the prayer record screen class '''

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen


class PrayerRecordsScreen(Screen):
	''' Screen to show today's record list '''

	record_lists = ObjectProperty()

	def on_pre_enter(self):
		''' Ready the screen for display '''
		self.record_lists.create_lists()
	
	def on_pre_leave(self):
		''' Destory all data before upon leaving the screen '''
		self.record_lists.destroy_lists()
