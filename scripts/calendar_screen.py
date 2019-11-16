'''Module for all the calendar related classes and functionality'''

import calendar
import datetime

from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

import constants
import convertdate.islamic as islamic
from custom_widgets import CustomModalView, TextButton

MONTHS = ["January", "Feburary", "March", "April", "May", "June", "July",
		"August", "September", "October", "November", "December"]

ISLAMIC_MONTHS = ("Muharram", "Safar", "Rabi' al-Awwal", "Rabi' ath-Thani",
			"Jumada al-Ula", "Jumada al-Akhirah", "Rajab", "Sha'ban",
			"Ramadan", "Shawwal", "Dhu al-Qa‘dah", "Dhu al-Hijjah")


class CalendarScreen(Screen):
	'''Screen providing a calendar to go through and change or view any dates's records'''

	islamic_month_year = ObjectProperty()
	cal = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.bind(on_pre_enter=lambda _: self.create_calendar_screen())
		self.bind(on_leave=lambda _: self.cal.destroy_calendar())

	def create_calendar_screen(self):
		'''Create the calendar screen and load the data required for function'''
		self.cal.populate_func = self.populate_calendar
		self.cal.date_widget = DateButton
		self.hijri_adjustment = int(App.get_running_app().settings["hijri_adjustment"])
		self.cal.create_calendar()

	def set_islamic_month_text(self):
		'''Find the current month's islamic equivalent and set the text to that range'''
		hijri_start = islamic.from_gregorian(self.cal.year, self.cal.month, 1, adj=self.hijri_adjustment)
		hijri_end = islamic.from_gregorian(self.cal.year, self.cal.month,
										calendar.monthrange(self.cal.year, self.cal.month)[1], adj=self.hijri_adjustment)

		start = f"{hijri_start[2]} {ISLAMIC_MONTHS[hijri_start[1] - 1]}"
		end = f"{hijri_end[2]} {ISLAMIC_MONTHS[hijri_end[1] - 1]}"
		self.islamic_month_year.text = start + " - " + end

	def populate_calendar(self):
		'''Create the calendar dates for the screen and set the month and year texts'''

		self.set_islamic_month_text()
		self.cal.set_month_year_text()
		
		# initialize the dates data so conflict does not happen
		self.cal.dates.data = []

		month = self.cal.get_month_list()
		for day in month:
			if not day:
				# Make an empty widget if the date doesn't exist
				self.cal.dates.data.append({"text": "", "background_color": constants.GREY_COLOR, "editable": False})
			else:
				date = datetime.date(self.cal.year, self.cal.month, day)

				# If date is of the future make the popup uneditable
				if date > datetime.date.today():
					editable = False
				else:
					editable = True

				# Color the button
				if date == datetime.date.today():
					bg_color = constants.WARNING_COLOR
				else:
					bg_color = constants.MAIN_COLOR

				self.cal.dates.data.append({"text": str(day), "editable": editable, "date": date, "background_color": bg_color})


class DateButton(TextButton):
	'''Button for a day in a month'''

	def __init__(self, date=None, editable=True, **kwargs):
		super().__init__(**kwargs)
		self.date = date
		self.editable = editable

	def on_press(self):
		'''Display the popup with prayer record of the date'''
		if self.editable:
			RecordsPopup(self.date).open()
		else:
			self.state = "normal"


class Calendar(BoxLayout):
	'''Calendar Widget displaying all the days in a month with buttons'''
	month_year_button = ObjectProperty()
	dates = ObjectProperty()
	weekdays = ObjectProperty()
	date_widget = ObjectProperty()
	populate_func = ObjectProperty()

	def __init__(self, populate_func=None, **kwargs):
		super().__init__(**kwargs)
		d = datetime.date.today()

		self.year, self.month, self.day = d.year, d.month, d.day

	def create_calendar(self):
		'''Create the calendar date buttons and week labels and required popups'''
		self.month_popup = MonthPopup(cal=self)
		self.populate_func()

	def destroy_calendar(self):
		'''Remove all the dates and week widgets and required popups'''
		self.month_popup = None
		self.dates.data = []

	def set_month_year_text(self):
		'''Put the current month and year text onto the month year button'''
		self.month_year_button.text = f"{MONTHS[self.month - 1]} {self.year}"

	def get_month_list(self):
		'''Get the current month calendar as a list of dates'''
		month = calendar.monthcalendar(self.year, self.month)
		return [day for week in month for day in week]
	
	def previous_month(self):
		'''Move back one month'''
		self.year, self.month = calendar.prevmonth(self.year, self.month)
		self.populate_func()

	def next_month(self):
		'''Move one month forward'''
		self.year, self.month = calendar.nextmonth(self.year, self.month)
		self.populate_func()

	def change_month(self, value):
		'''Change the month to chosen month'''
		self.month = value

	def previous_year(self):
		'''Move one year back'''
		self.change_year(int(self.year) - 1)
	
	def next_year(self):
		'''Move one year forward'''
		self.change_year(int(self.year) + 1)

	def change_year(self, value):
		'''Change the year to chosen year'''
		self.year = int(value)
		self.month_popup.year = str(value)

	def open_month_popup(self):
		'''Open a new month popup'''
		self.month_popup.year = str(self.year)
		self.month_popup.open()


class RecordsPopup(CustomModalView):
	'''Popup displaying prayer and other records for each date'''
	record_lists = ObjectProperty()
	
	def __init__(self, date=None,**kwargs):
		super().__init__(**kwargs)
		
		self.record_lists.date = date
		self.bind(on_pre_open=lambda _: self.record_lists.create_lists())
		self.bind(on_dismiss=lambda _: self.record_lists.destroy_lists())


class YearPopup(CustomModalView):
	'''Popup to select year for the calendar'''
	year_grid = ObjectProperty()
	calendar = ObjectProperty()
	year_range = StringProperty("")
	min_year = NumericProperty()
	max_year = NumericProperty()

	def __init__(self, cal=None, **kwargs):
		super().__init__(**kwargs)
		self.calendar = cal

		self.bind(on_pre_open=lambda _: self.create_year_grid())
		self.bind(on_dismiss=lambda _: self.destroy_year_grid())

	def set_year_range(self, year):
		'''Set the range of years to be displayed'''
		self.max_year = int(year)
		self.min_year = self.max_year - 11
		self.stringify_year_range()

	def stringify_year_range(self):
		'''Assign a string value to year range from min_year and max_year'''
		self.year_range = '-'.join((str(self.min_year), str(self.max_year)))

	def next_year_range(self):
		'''Move the range to next ten years'''
		self.min_year = self.max_year
		self.max_year = self.min_year + 11
		self.stringify_year_range()
		self.create_year_grid()

	def previous_year_range(self):
		'''Move the range to previous ten years'''
		self.max_year = self.min_year
		self.min_year = self.min_year - 11
		self.stringify_year_range()
		self.create_year_grid()

	def create_year_grid(self):
		'''Create year buttons from the year range'''
		if not self.min_year:
			raise ValueError("0 is not a valid value for min_year")
		elif not self.max_year:
			raise ValueError("0 is not a valid value for max_year")

		year_range = range(self.min_year, self.max_year + 1)
		self.year_grid.data = [{"calendar": self.calendar, "text": str(year)} for year in year_range]

	def destroy_year_grid(self):
		'''Erase all data from popup'''
		self.year_grid.data = {}
		self.year_range = ""
	

class MonthPopup(CustomModalView):
	'''Popup to select month for the calendar'''
	month_grid = ObjectProperty()
	year = StringProperty("")
	calendar = ObjectProperty()

	def __init__(self, cal=None, **kwargs):
		super().__init__(**kwargs)
		self.calendar = cal

		self.bind(on_pre_open=lambda _: self.create_month_grid())
		self.bind(on_pre_dismiss=lambda _: self.calendar.populate_func())
		self.bind(on_dismiss=lambda _: self.destroy_month_grid())

	def create_month_grid(self):
		'''Create the month grid on the popup and the year popup'''
		if not self.year:
			raise ValueError("Year Value cannot be none")
		elif not self.calendar:
			raise ValueError("Calendar object cannot be none")

		self.year_popup = YearPopup(cal=self.calendar)
		self.month_grid.data = [{"calendar": self.calendar, "text": month} for month in MONTHS]

	def destroy_month_grid(self):
		'''Remove the month grid and other data from the popup'''
		self.month_grid.data = {}
		self.year_popup = None
		self.year = ""

	def open_year_popup(self):
		'''Open the year popup with the current year for selection'''
		self.year_popup.set_year_range(self.year)
		self.year_popup.open()


class YearButton(TextButton):
	'''Button for the Year Popup grid'''
	calendar = ObjectProperty()
	
	def __init__(self, cal=None, **kwargs):
		super().__init__(**kwargs)
		self.calendar = cal

	def on_text(self, instance, value):
		'''When month is given a name then give it focus if it is the current month and instantiate the month's number'''
		self.year = int(value)
		if self.calendar.year == self.year:
			self.background_color = constants.SECONDRY_COLOR
		else:
			self.background_color = constants.MAIN_COLOR

	def on_press(self):
		'''Change the calendar's year to the year selected if it is not the current year'''
		if self.calendar.year != self.year:
			self.calendar.month_popup.year_popup.dismiss()
			self.calendar.change_year(self.year)


class MonthButton(TextButton):
	'''Button for the Month Popup grid'''
	calendar = ObjectProperty()
	
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def on_text(self, instance, value):
		'''When month is given a name then give it focus if it is the current month and instantiate the month's number'''
		self.month_no = MONTHS.index(value) + 1
		if self.calendar.month == self.month_no:
			self.background_color = constants.SECONDRY_COLOR
		else:
			self.background_color = constants.MAIN_COLOR

	def on_press(self):
		'''Change the current month of the calendar if the selected button is not current month'''
		if self.calendar.month != self.month_no:
			self.calendar.change_month(self.month_no)
			self.calendar.month_popup.dismiss()
