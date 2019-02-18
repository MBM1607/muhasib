''' Module for all the calendar related classes and functionality '''

import calendar
import datetime

from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty, DictProperty
from kivy.uix.button import Button
from kivy.app import App
from kivy.lang.builder import Builder

from custom_widgets import CustomButton, BlackLabel, CustomPopup, CustomDropDown

import convertdate.islamic as islamic


Builder.load_file("scripts/calendar.kv")

MONTHS = ["January", "Feburary", "March", "April", "May", "June", "July",
		"August", "September", "October", "November", "December"]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ISLAMIC_WEEKDAYS = ("al-'ahad", "al-'ithnayn",
					"ath-thalatha'", "al-'arb`a'",
					"al-khamis", "al-jum`a", "as-sabt")

ISLAMIC_MONTHS = ("Muharram", "Safar", "Rabi' al-Awwal", "Rabo' ath-Thani ",
			"Jumada al-Ula", "Jumada al-Akhirah", "Rajab", "Sha'ban",
			"Ramadan", "Shawwal", "Dhu al-Qa‘dah", "Dhu al-Hijjah")


class DatePopup(CustomPopup):
	''' Popup displaying prayer record for each date '''
	salah_list = ObjectProperty()


class MonthDropDown(CustomDropDown):
	''' Drop down list for months '''
	months = ListProperty(MONTHS)


class DateButton(CustomButton):
	''' Button for a day in a month '''
	prayer_record = DictProperty()

	def __init__(self, date=None, editable=True, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.date = date
		self.editable = editable
		self.popup = DatePopup()

		self.color_button()

	def get_date(self):
		if self.app.calendar.islamic:
			date = islamic.to_gregorian(self.date.year, self.date.month, self.date.day)
			return datetime.date(*date)
		else:
			return self.date

	def color_button(self):
		''' Color the button based on special conditions of the date '''

		if self.get_date() == self.app.today:
			self.background_colors = ((191, 69, 49, 220), (161, 39, 19, 255))
		elif self.get_date().weekday() == 4:
			self.background_colors = ((14, 160, 31, 220), (0, 120, 0, 255))

	def on_press(self):
		'''  Display the popup with prayer record of the date '''
		if not self.prayer_record:
			self.get_prayer_record()

		times_data = self.app.prayer_times.get_times(self.get_date())
		self.popup.salah_list.data = [{"name": n.capitalize(), "time": t} for n, t in times_data.items() if n in ["fajr", "dhuhr", "asr", "maghrib", "isha"]]
		for x in self.popup.salah_list.data:
			x["record"] = self.prayer_record[x["name"].lower()]
			x["base"] = self
			x["editable"] = self.editable
		self.popup.open()

	def get_prayer_record(self):
		''' Get the prayer_record of the date from the database '''
		self.app.database.create_prayer_record(self.get_date())
		prayer_record = self.app.database.get_prayer_record(self.get_date())
		self.prayer_record = {"fajr": prayer_record[2], "dhuhr": prayer_record[3], "asr": prayer_record[4],
							"maghrib": prayer_record[5], "isha": prayer_record[6]}

	def on_prayer_record(self, instance, value):
		''' Refresh the prayer_records when changed '''
		self.update_salah_buttons_record()
		self.app.database.update_prayer_record(self.get_date(), **self.prayer_record)

	def update_salah_buttons_record(self):
		''' Change the record on individual labels '''
		for x in self.popup.salah_list.children[0].children:
			x.record = self.prayer_record[x.name.lower()]


class Calendar(ModalView):
	''' Class to hold all the calendar functionality '''

	year_menu = StringProperty("Year")
	month_menu = ObjectProperty()
	days = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		d = datetime.datetime.today()
		self.year, self.month, self.day = d.year, d.month, d.day

		# Create the dropdown and bind the functionality
		self.month_dropdown = MonthDropDown()
		self.month_menu.bind(on_release=self.month_dropdown.open)
		self.month_dropdown.bind(on_select=self.change_month)

		self.islamic = False

	def populate(self):
		''' Create the current month and year's calendar '''
		self.month_menu.text = self.month_dropdown.months[self.month-1]
		self.year_menu = str(self.year)
		self.dates.populate(self.year, self.month)
	
	def previous_month(self):
		''' Move back one month '''
		self.year, self.month = calendar.prevmonth(self.year, self.month)
		self.populate()

	def next_month(self):
		''' Move one month forward '''
		self.year, self.month = calendar.nextmonth(self.year, self.month)
		self.populate()

	def change_month(self, instance, value):
		''' Change the month '''
		self.month = value
		self.populate()

	def next_year(self):
		''' Move to next year '''
		self.year += 1
		self.populate()
	
	def previous_year(self):
		''' Move to previous year '''
		self.year -= 1
		self.populate()

	def convert_to_islamic(self):
		''' Converts the gregorian calendar to islamic calendar using current date '''
		if not self.islamic:
			self.month_dropdown.months = ISLAMIC_MONTHS
			self.days.weekdays = ISLAMIC_WEEKDAYS
			self.year, self.month, self.day = islamic.from_gregorian(self.year, self.month, self.day)
			self.islamic = True
			self.populate()

	def convert_to_gregorian(self):
		''' Converts the islamic calendar to gregorian calendar using current date '''
		if self.islamic:
			self.month_dropdown.months = MONTHS
			self.days.weekdays = WEEKDAYS
			self.year, self.month, self.day = islamic.to_gregorian(self.year, self.month, self.day)
			self.islamic = False
			self.populate()


class Days(BoxLayout):
	''' Class to layout the day's labels in a month '''
	weekdays = ListProperty(WEEKDAYS)

class Dates(GridLayout):
	''' Class to layout the day of a month '''

	def populate(self, year, month):
		''' Create the dates buttons according to year and month '''
		cal = self.parent.parent
		app = App.get_running_app()

		self.clear_widgets()
		if cal.islamic:
			dates = islamic.monthcalendar(year, month)
		else:
			dates = calendar.monthcalendar(year, month)
		for i in dates:
			for j in i:
				if not j:
					self.add_widget(Widget())
				else:
					day = int(f"{j}")
					date = datetime.date(cal.year, cal.month, day)
					# If date is of the future make the popup uneditable
					if date > app.today:
						editable = False
					else:
						editable = True
					self.add_widget(DateButton(text=f"{j}", date=date, editable=editable))
