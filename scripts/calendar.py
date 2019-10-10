''' Module for all the calendar related classes and functionality '''

import calendar
import datetime

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen

import constants
import convertdate.islamic as islamic
from custom_widgets import CustomButton, CustomDropDown, CustomPopup

MONTHS = ["January", "Feburary", "March", "April", "May", "June", "July",
		"August", "September", "October", "November", "December"]


ISLAMIC_MONTHS = ("Muharram", "Safar", "Rabi' al-Awwal", "Rabo' ath-Thani ",
			"Jumada al-Ula", "Jumada al-Akhirah", "Rajab", "Sha'ban",
			"Ramadan", "Shawwal", "Dhu al-Qa‘dah", "Dhu al-Hijjah")


class RecordsPopup(CustomPopup):
	''' Popup displaying prayer and other records for each date '''
	record_lists = ObjectProperty()


class MonthDropDown(CustomDropDown):
	''' Drop down list for months '''
	months = ListProperty(MONTHS)


class DateButton(CustomButton):
	''' Button for a day in a month '''

	def __init__(self, date=None, editable=True, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.date = date
		self.editable = editable
		self.popup = RecordsPopup()
		self.popup.record_lists.date = self.get_date()

		self.color_button()

	def get_date(self):
		if self.app.calendar.islamic:
			date = islamic.to_gregorian(self.date.year, self.date.month, self.date.day)
			return datetime.date(*date)
		else:
			return self.date

	def color_button(self):
		''' Color the button based on special conditions of the date '''

		if self.get_date() == datetime.date.today():
			self.background_color = constants.WARNING_COLOR
		elif islamic.from_gregorian(self.get_date().year, self.get_date().month, self.get_date().day)[1] == 9:
			self.background_color = constants.SECONDRY_COLOR

	def on_press(self):
		'''  Display the popup with prayer record of the date '''
		if self.editable:
			self.popup.record_lists.create_lists()
			self.popup.open()


class Calendar(Screen):
	''' Class to hold all the calendar functionality '''

	year_menu = StringProperty("Year")
	month_menu = ObjectProperty()
	dates = ObjectProperty()
	days = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		d = datetime.date.today()
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
			self.year, self.month, self.day = islamic.from_gregorian(self.year, self.month, self.day)
			self.islamic = True
			self.populate()

	def convert_to_gregorian(self):
		''' Converts the islamic calendar to gregorian calendar using current date '''
		if self.islamic:
			self.month_dropdown.months = MONTHS
			self.year, self.month, self.day = islamic.to_gregorian(self.year, self.month, self.day)
			self.islamic = False
			self.populate()


class Days(BoxLayout):
	''' Class to layout the day's labels in a month '''
	weekdays = ListProperty(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])


class Dates(GridLayout):
	''' Class to layout the day of a month '''

	def populate(self, year, month):
		''' Create the dates buttons according to year and month '''
		cal = self.parent.parent.parent
		today = datetime.date.today()
	
		self.clear_widgets()
		if cal.islamic:
			dates = islamic.monthcalendar(year, month)
			today = islamic.from_gregorian(today.year, today.month, today.day)
			today = datetime.date(today[0], today[1], today[2])
		else:
			dates = calendar.monthcalendar(year, month)
		for i in dates:
			for j in i:
				if not j:
					self.add_widget(Widget())
				else:
					date = datetime.date(cal.year, cal.month, j)
					# If date is of the future make the popup uneditable
					if date > today:
						editable = False
					else:
						editable = True
					self.add_widget(DateButton(text=f"{j}", date=date, editable=editable))
