''' Module for all the calendar related classes and functionality '''

import calendar
import datetime

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen

import constants
import convertdate.islamic as islamic
from custom_widgets import CustomButton, CustomPopup, CustomModalView

MONTHS = ["January", "Feburary", "March", "April", "May", "June", "July",
		"August", "September", "October", "November", "December"]


ISLAMIC_MONTHS = ("Muharram", "Safar", "Rabi' al-Awwal", "Rabo' ath-Thani ",
			"Jumada al-Ula", "Jumada al-Akhirah", "Rajab", "Sha'ban",
			"Ramadan", "Shawwal", "Dhu al-Qa‘dah", "Dhu al-Hijjah")


class Calendar(Screen):
	''' Class to hold all the calendar functionality '''

	month_year_button = ObjectProperty()
	dates = ObjectProperty()
	weekdays = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		d = datetime.date.today()
		self.year, self.month, self.day = d.year, d.month, d.day

		self.islamic = False

	def on_pre_enter(self):
		''' Ready the screen for display '''
		self.month_popup = MonthPopup()
		self.weekdays.data = [{"text": day} for day in ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")]
		self.populate()

	def on_pre_leave(self):
		''' Delete all widgets from the screen '''
		self.month_popup = None
		self.dates.clear_widgets()

	def populate(self):
		''' Create the current month and year's calendar '''
		print(islamic.from_gregorian(self.year, self.month, self.day))
		self.month_year_button.text = MONTHS[self.month - 1] + ' ' + str(self.year)
		self.dates.populate(self.year, self.month)
	
	def previous_month(self):
		''' Move back one month '''
		self.year, self.month = calendar.prevmonth(self.year, self.month)
		self.populate()

	def next_month(self):
		''' Move one month forward '''
		self.year, self.month = calendar.nextmonth(self.year, self.month)
		self.populate()

	def change_month(self, value):
		''' Change the month to chosen month '''
		self.month = value

	def previous_year(self):
		''' Move one year back '''
		self.change_year(int(self.year) - 1)
	
	def next_year(self):
		''' Move one year forward '''
		self.change_year(int(self.year) + 1)

	def change_year(self, value):
		''' Change the year to chosen year '''
		self.year = int(value)
		self.month_popup.year = str(value)

	def open_month_popup(self):
		''' Open a new month popup '''
		self.month_popup.year = str(self.year)
		self.month_popup.open()

	def convert_to_islamic(self):
		''' Converts the gregorian calendar to islamic calendar using current date '''
		if not self.islamic:
			self.year, self.month, self.day = islamic.from_gregorian(self.year, self.month, self.day)
			self.islamic = True
			self.populate()

	def convert_to_gregorian(self):
		''' Converts the islamic calendar to gregorian calendar using current date '''
		if self.islamic:
			self.year, self.month, self.day = islamic.to_gregorian(self.year, self.month, self.day)
			self.islamic = False
			self.populate()


class Weekdays(BoxLayout):
	''' Class to layout the day's labels in a month '''
	pass


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


class RecordsPopup(CustomPopup):
	''' Popup displaying prayer and other records for each date '''
	record_lists = ObjectProperty()


class YearPopup(CustomModalView):
	''' Popup to select year for the calendar '''
	year_grid = ObjectProperty()
	year_range = StringProperty("")
	min_year = NumericProperty()
	max_year = NumericProperty()
	
	def set_year_range(self, year):
		''' Set the range of years to be displayed '''
		self.max_year = int(year)
		self.min_year = self.max_year - 11
		self.stringify_year_range()

	def stringify_year_range(self):
		''' Assign a string value to year range from min_year and max_year '''
		self.year_range = '-'.join((str(self.min_year), str(self.max_year)))

	def next_year_range(self):
		''' Move the range to next ten years '''
		self.min_year = self.max_year
		self.max_year = self.min_year + 11
		self.stringify_year_range()
		self.create_year_grid()

	def previous_year_range(self):
		''' Move the range to previous ten years '''
		self.max_year = self.min_year
		self.min_year = self.min_year - 11
		self.stringify_year_range()
		self.create_year_grid()

	def create_year_grid(self):
		''' Create year buttons from the year range '''
		assert self.min_year, "0 is not a valid year"
		assert self.max_year, "0 is not a valid year"
		self.year_grid.data = [{"text": str(year)} for year in range(self.min_year, self.max_year + 1)]

	def on_pre_open(self):
		''' Ready the poup to be displayed '''
		self.create_year_grid()
	
	def on_pre_dismiss(self):
		''' Erase all data from the popup before it is dismissed '''
		self.year_grid.data = {}
		self.year_range = ""
	

class MonthPopup(CustomModalView):
	''' Popup to select month for the calendar '''
	month_grid = ObjectProperty()
	year = StringProperty("")

	def open_year_popup(self):
		''' Open the year popup with the current year for selection '''
		self.year_popup.set_year_range(self.year)
		self.year_popup.open()

	def on_pre_open(self):
		''' Populate the popup with months and ready it to be opened '''
		assert self.year
		self.year_popup = YearPopup()
		self.month_grid.data = [{"text": month} for month in MONTHS]
	
	def on_pre_dismiss(self):
		''' Erase all data from the popup before it is dismissed '''
		self.month_grid.data = {}
		self.year_popup = None
		self.year = ""
		App.get_running_app().calendar.populate()


class YearButton(CustomButton):
	''' Button for the Year Popup grid '''
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.calendar = App.get_running_app().calendar

	def on_text(self, instance, value):
		''' When month is given a name then give it focus if it is the current month and instantiate the month's number '''
		self.year = int(value)
		if self.calendar.year == self.year:
			self.background_color = constants.SECONDRY_COLOR
		else:
			self.background_color = constants.MAIN_COLOR

	def on_press(self):
		''' Handle the pressing of MonthButton '''
		if self.calendar.year != self.year:
			self.calendar.month_popup.year_popup.dismiss()
			self.calendar.change_year(self.year)


class MonthButton(CustomButton):
	''' Button for the Month Popup grid '''
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.calendar = App.get_running_app().calendar

	def on_text(self, instance, value):
		''' When month is given a name then give it focus if it is the current month and instantiate the month's number '''
		self.month_no = MONTHS.index(value) + 1
		if self.calendar.month == self.month_no:
			self.background_color = constants.SECONDRY_COLOR
		else:
			self.background_color = constants.MAIN_COLOR

	def on_press(self):
		''' Handle the pressing of MonthButton '''
		if self.calendar.month != self.month_no:
			self.calendar.change_month(self.month_no)
			self.calendar.month_popup.dismiss()
