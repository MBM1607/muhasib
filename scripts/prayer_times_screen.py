'''Module to hold the class PrayerTimesScreen'''

from datetime import date, datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty

from constants import MAIN_COLOR, SECONDRY_COLOR
from custom_widgets import CustomScreen, DoubleTextButton
from helpers import notify


class PrayerTimesScreen(CustomScreen):
	'''Class for the screen to show the prayer times'''
	times_list = ObjectProperty()
	prayer_time_left = ObjectProperty()
	next_prayer = ObjectProperty()
	current_time = ObjectProperty()
	location = ObjectProperty()

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.app = App.get_running_app()
		self.prayer_times = {}

		self.bind(on_pre_enter=lambda _: self.create_prayers_data())
		self.bind(on_leave=lambda _: self.destroy_prayer_data())

	def refresh(self):
		'''Refresh the screen'''
		self.create_prayers_data()

	def create_prayers_data(self):
		'''Create the prayer times data and schedule the upgrade event'''
		if self.app.location_data_present():
			self.update_prayer_times()

			self.update_clock_event = Clock.schedule_interval(lambda _: self.update_prayer_labels(), 30)
			self.location.text = self.app.settings["location"]
		else:
			notify(title="Location Needed", message="Location is needed to calculate the prayer times")

	def destroy_prayer_data(self):
		'''Remove all prayer data from the screen and cancel the upgrade event'''
		if self.app.location_data_present():
			self.update_clock_event.cancel()
			self.times_data = {}
			self.prayer_times = {}
			self.times_list.data = []
			self.current_time.text = ""
			self.location.text = ""
			self.next_prayer.text = ""

	def update_prayer_times(self):
		'''Update the prayer times'''

		# Calculate today's prayer times
		self.times_data = self.app.prayer_times.get_times(date.today())

		# Populate the lists on the dashboard
		self.times_list.data = [{"name": n.capitalize(), "info": t} for n, t in self.times_data.items()]

		self.update_prayer_labels()

	def focus_next_prayer(self, next_prayer):
		'''Put focus on the next prayer so it can be highlighted'''
		for prayer in self.times_list.data:
			if prayer["name"] == next_prayer:
				prayer["background_color"] = SECONDRY_COLOR
			else:
				prayer["background_color"] = MAIN_COLOR

	def update_prayer_labels(self):
		'''Change the labels reporting information about prayers'''

		# Get just the current hour and minutes
		current_time = datetime.strptime(datetime.strftime(self.app.get_current_time(), "%H:%M"), "%H:%M")
		self.current_time.text = "Current Time: " + self.app.get_formatted_time(self.app.get_current_time())

		# Measure the time remaining in all prayers
		prayers_left = []
		for name, prayer_time in self.times_data.items():
			if not prayer_time == "----":
				if self.app.prayer_times.time_format == "12h":
					prayer_time = datetime.strptime(prayer_time, "%I:%M %p")
				else:
					prayer_time = datetime.strptime(prayer_time, "%H:%M ")

				if prayer_time > current_time:
					dt = prayer_time - current_time
					dt = (datetime.min + dt).time()
					if dt.hour == 0:
						dt_str = dt.strftime("%M minutes remaining")
					else:
						dt_str = dt.strftime("%H hours & %M minutes remaining")
					prayers_left.append((dt_str, name, prayer_time))
					self.prayer_times[name] = dt_str
				else:
					dt = (current_time - prayer_time)
					dt = (datetime.min + dt).time()
					if dt.hour == 0:
						dt_str = dt.strftime("Was %M minutes ago")
					else:
						dt_str = dt.strftime("Was %H hours & %M minutes ago")

					self.prayer_times[name] = dt_str

		if prayers_left:
			time_left, next_prayer, prayer_time = min(prayers_left, key=lambda prayer: prayer[2])
			self.prayer_time_left.text = time_left
			# Set the next prayer text
			self.next_prayer.text = next_prayer.capitalize() + ": " + self.app.get_formatted_time(prayer_time)
			# Put colored focus on the next prayer time
			self.focus_next_prayer(next_prayer.split(":")[0].capitalize())
		else:
			self.prayer_time_left.text = ""
			self.next_prayer.text = ""

	def display_notification(self, prayer):
		'''Display the prayer toast notification'''

		notify(title=prayer, message=self.prayer_times[prayer.lower()], timeout=2)


class PrayerButton(DoubleTextButton):
	'''Button to display prayer time and display time left or past upon being clicked'''

	def on_press(self):
		'''Display the toast notification with the time left in the current prayer or the time past'''
		screen = App.get_running_app().screen_manager.current_screen
		screen.display_notification(self.name)
