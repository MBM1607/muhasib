import calendar
import datetime

from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder

Builder.load_file("scripts/calendar.kv")

class Empty(Widget):
	pass

class CalendarButton(Button):
	pass

class Calendar(ModalView):
	title = StringProperty("Year Month")

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		d = datetime.datetime.today()
		self.year, self.month = d.year, d.month
		self.populate()
		

	def populate(self):
		month = calendar.month(self.year, self.month)
		month = [x.strip() for x in month.split("\n")]
		self.title = month[0]
		self.days.days = month[1].split()
		self.dates.populate(self.year, self.month)

	def previous_month(self):
		self.year, self.month = calendar.prevmonth(self.year, self.month)
		self.populate()

	def next_month(self):
		self.year, self.month = calendar.nextmonth(self.year, self.month)
		self.populate()

class Days(BoxLayout):
	days = ListProperty(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"])

class Dates(GridLayout):
	def populate(self, year, month):
		self.clear_widgets()
		dates = calendar.monthcalendar(year, month)
		for i in dates:
			for j in i:
				if j == 0:
					self.add_widget(Empty())
				else:
					self.add_widget(CalendarButton(text=f"{j}"))
