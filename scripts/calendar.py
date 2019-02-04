import calendar
import datetime

from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.widget import Widget


class Empty(Widget):
	''' Empty spot on the calendar '''
	pass

class CalendarButton(Button):
	''' Basic button on the calendar screen '''
	pass

class DateButton(CalendarButton):
	''' Button for a day in a month '''
	def on_press(self):
		pass

class Calendar(ModalView):
	''' Class to hold all the calendar functionality '''

	title = StringProperty("Year Month")

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		d = datetime.datetime.today()
		self.year, self.month = d.year, d.month
		self.populate()
		
	# Create the current month and year's calendar
	def populate(self):
		month = calendar.month(self.year, self.month)
		month = [x.strip() for x in month.split("\n")]
		self.title = month[0]
		self.days.days = month[1].split()
		self.dates.populate(self.year, self.month)
	
	# Move back one month
	def previous_month(self):
		self.year, self.month = calendar.prevmonth(self.year, self.month)
		self.populate()

	# Move one month forward
	def next_month(self):
		self.year, self.month = calendar.nextmonth(self.year, self.month)
		self.populate()

class Days(BoxLayout):
	''' Class to layout the day's labels in a month '''
	days = ListProperty(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"])

class Dates(GridLayout):
	''' Class to layout the day of a month '''

	# Add the dates
	def populate(self, year, month):
		self.clear_widgets()
		dates = calendar.monthcalendar(year, month)
		for i in dates:
			for j in i:
				if j == 0:
					self.add_widget(Empty())
				else:
					self.add_widget(DateButton(text=f"{j}"))
