''' Module to hold the prayer record screen class '''

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen


class PrayerRecordsScreen(Screen):
	''' Screen to show today's record list '''

	record_lists = ObjectProperty()

	def create_lists(self):
		''' Dummy method to transfer the call to RecordLists to create record lists'''
		self.record_lists.create_lists()
