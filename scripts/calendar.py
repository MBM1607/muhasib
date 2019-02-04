''' Module for all the calendar related classes and functionality '''

import calendar
import datetime

from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty, DictProperty
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.app import App

from prayer_widgets import CustomPopup


class DatePopup(CustomPopup):
	''' Popup displaying prayer record for each date '''
	salah_list = ObjectProperty()

class Empty(Widget):
	''' Empty spot on the calendar '''
	pass

class CalendarButton(Button):
	''' Basic button on the calendar screen '''
	pass

class DateButton(CalendarButton):
	''' Button for a day in a month '''
	prayer_record = DictProperty()

	def __init__(self, date=None, editable=True, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.date = date
		self.editable = editable
		self.popup = DatePopup()

		# Get the prayer_record of the date
		self.app.database.create_prayer_record(self.date)
		prayer_record = self.app.database.get_prayer_record(self.date)
		self.prayer_record = {"fajr": prayer_record[2], "dhuhr": prayer_record[3], "asr": prayer_record[4],
						"maghrib": prayer_record[5], "isha": prayer_record[6]}

	# Display the popup with prayer record of the date
	def on_press(self):	
		times_data = self.app.prayer_times.get_times(self.date)
		self.popup.salah_list.data = [{"name": n.capitalize(), "time": t} for n, t in times_data.items() if n in ["fajr", "dhuhr", "asr", "maghrib", "isha"]]
		for x in self.popup.salah_list.data:
			x["record"] = self.prayer_record[x["name"].lower()]
			x["base"] = self
			x["editable"] = self.editable
		self.popup.open()

	# When prayer_record is changed
	def on_prayer_record(self, instance, value):
		self.update_salah_buttons_record()
		self.app.database.update_prayer_record(self.date, **self.prayer_record)

	def update_salah_buttons_record(self):
		for x in self.popup.salah_list.children[0].children:
			x.record = self.prayer_record[x.name.lower()]


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
		cal = self.parent.parent
		app = App.get_running_app()

		self.clear_widgets()
		dates = calendar.monthcalendar(year, month)
		for i in dates:
			for j in i:
				if j == 0:
					self.add_widget(Empty())
				else:
					date = datetime.date(cal.year, cal.month, int(f"{j}"))
					if date > app.today:
						editable = False
					else:
						editable = True
					self.add_widget(DateButton(text=f"{j}", date=date, editable=editable))
