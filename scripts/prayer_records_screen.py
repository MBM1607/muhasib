'''Module to hold the prayer record screen class'''

from datetime import date

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen


class PrayerRecordsScreen(Screen):
	'''Screen to show today's record list'''

	record_lists = ObjectProperty()
	datepicker = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.bind(on_pre_enter=lambda _: self.create_record_lists())
		self.bind(on_leave=lambda _: self.record_lists.destroy_lists())

	def create_record_lists(self):
		'''Create the prayer record list and set the datepicker to the current day'''
		self.datepicker.date = date.today()

	def change_date(self):
		'''Change the date of the prayer record's being showen'''
		if self.datepicker.text:
			self.record_lists.change_date(self.datepicker.date)
